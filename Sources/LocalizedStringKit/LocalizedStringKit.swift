//
//  Copyright (c) Microsoft Corporation. All rights reserved.
//

import CommonCrypto
import Foundation

// MARK: - Core

/// Backing implementation for LocalizedStringKit.
///
/// This holds all mutable global state (the primary bundle name, the alternate
/// search path and the bundle cache) behind a lock so that concurrent
/// `Localized(...)` calls are safe.
final class LocalizedStringKitCore {

    /// Shared singleton.
    static let shared = LocalizedStringKitCore()

    /// The table name is fixed and does not change between bundles.
    private static let table = "LocalizedStringKit"

    /// Guards `primaryBundleName`, `alternateBundleSearchPath` and the caches.
    private let lock = NSLock()

    private var _primaryBundleName = "LocalizedStringKit.bundle"
    private var _alternateBundleSearchPath: URL?

    /// Cache of resolved bundles keyed by bundle name.
    private var bundleCache: [String: Bundle] = [:]

    /// Names we already tried to resolve and failed. Mirrors the original
    /// `NSNull` sentinel so we don't repeatedly hit the filesystem.
    private var knownMissing: Set<String> = []

    var primaryBundleName: String {
        get {
            lock.lock()
            defer { lock.unlock() }
            return _primaryBundleName
        }
        set {
            lock.lock()
            _primaryBundleName = newValue
            lock.unlock()
        }
    }

    var alternateBundleSearchPath: URL? {
        get {
            lock.lock()
            defer { lock.unlock() }
            return _alternateBundleSearchPath
        }
        set {
            lock.lock()
            _alternateBundleSearchPath = newValue
            // The cache depends on the search path, so invalidate it.
            bundleCache.removeAll()
            knownMissing.removeAll()
            lock.unlock()
        }
    }

    /// Localize a value.
    ///
    /// - Parameters:
    ///   - value: The English string.
    ///   - comment: Context for translators.
    ///   - keyExtension: Optional string to differentiate homographs.
    ///   - bundleName: Optional bundle name. Defaults to the primary bundle.
    /// - Returns: The localized string, or `value` if no bundle/entry is found.
    func localize(value: String, comment: String, keyExtension: String?, bundleName: String?) -> String {
        let key = Self.key(value: value, keyExtension: keyExtension)

        lock.lock()

        let effectiveBundleName = bundleName ?? _primaryBundleName

        if knownMissing.contains(effectiveBundleName) {
            lock.unlock()
            return value
        }

        var bundle = bundleCache[effectiveBundleName]

        if bundle == nil {
            bundle = Self.loadBundle(
                named: effectiveBundleName,
                alternateSearchPath: _alternateBundleSearchPath,
                primaryBundleName: _primaryBundleName
            )

            guard let resolved = bundle else {
                knownMissing.insert(effectiveBundleName)
                lock.unlock()
                return value
            }

            bundleCache[effectiveBundleName] = resolved
        }

        let resolvedBundle = bundle!
        lock.unlock()

        return resolvedBundle.localizedString(forKey: key, value: value, table: Self.table)
    }

    /// Resolve the bundle for the given name, honoring the alternate search path.
    func bundle(named bundleName: String?) -> Bundle? {
        lock.lock()
        let alternate = _alternateBundleSearchPath
        let primary = _primaryBundleName
        lock.unlock()

        let name = bundleName ?? primary
        return Self.loadBundle(named: name, alternateSearchPath: alternate, primaryBundleName: primary)
    }

    // MARK: Static helpers

    /// Generate the localization `key`.
    ///
    /// The key is `MD5(<value>)` or `MD5(<value>:<keyExtension>)`, hex-encoded.
    /// This logic must stay in sync with the generation tool.
    static func key(value: String, keyExtension: String?) -> String {
        var hashInput = value

        if let keyExtension = keyExtension, !keyExtension.isEmpty {
            hashInput += ":\(keyExtension)"
        }

        let data = Data(hashInput.utf8)
        var digest = [UInt8](repeating: 0, count: Int(CC_MD5_DIGEST_LENGTH))

        // Hash the full UTF-8 byte length. This must match the generator, which
        // hashes the entire string.
        _ = data.withUnsafeBytes { buffer in
            CC_MD5(buffer.baseAddress, CC_LONG(buffer.count), &digest)
        }

        return digest.map { String(format: "%02x", $0) }.joined()
    }

    /// Search for a strings bundle, mirroring the original upward search.
    private static func loadBundle(
        named bundleName: String,
        alternateSearchPath: URL?,
        primaryBundleName: String
    ) -> Bundle? {
        var name = bundleName
        if !name.hasSuffix(".bundle") {
            name += ".bundle"
        }

        // Alternate path check, if a URL is specified.
        if let alternateSearchPath = alternateSearchPath {
            let alternateBundleURL = alternateSearchPath.appendingPathComponent(name)
            if let bundle = Bundle(url: alternateBundleURL) {
                return bundle
            }
        }

        // Primary search path: walk up from the main bundle URL.
        var searchPath = Bundle.main.bundleURL

        while true {
            let bundleURL = searchPath.appendingPathComponent(name)

            if let bundle = Bundle(url: bundleURL) {
                if bundle.bundleURL.lastPathComponent == name {
                    return bundle
                }
                break
            }

            let newPath = searchPath.appendingPathComponent("..").standardizedFileURL

            if newPath == searchPath {
                break
            }

            searchPath = newPath
        }

        return nil
    }
}

// MARK: - Global configuration (Swift)

/// The name to be used for the primary strings bundle.
///
/// Example: `"LocalizedStringKit.bundle"`.
public var LSKPrimaryBundleName: String {
    get { LocalizedStringKitCore.shared.primaryBundleName }
    set { LocalizedStringKitCore.shared.primaryBundleName = newValue }
}

/// URL for alternate string bundle search (the root from where the search begins).
public var LSKAlternateBundleSearchPath: URL? {
    get { LocalizedStringKitCore.shared.alternateBundleSearchPath }
    set { LocalizedStringKitCore.shared.alternateBundleSearchPath = newValue }
}

// MARK: - Public API (Swift free functions)

/// Primary localization function used to localize strings.
///
/// - Parameters:
///   - value: The English string.
///   - comment: Context describing where the value is used.
public func Localized(_ value: String, _ comment: String) -> String {
    LocalizedStringKitCore.shared.localize(value: value, comment: comment, keyExtension: nil, bundleName: nil)
}

/// Localize a string in a specific bundle.
///
/// - Parameters:
///   - value: The English string.
///   - comment: Context describing where the value is used.
///   - bundleName: Bundle used to segment groups of strings.
public func LocalizedWithBundle(_ value: String, _ comment: String, _ bundleName: String) -> String {
    LocalizedStringKitCore.shared.localize(value: value, comment: comment, keyExtension: nil, bundleName: bundleName)
}

/// Localize a string with a key extension to disambiguate homographs.
///
/// - Parameters:
///   - value: The English string.
///   - comment: Context describing where the value is used.
///   - keyExtension: Included when generating the key, so two calls with the
///     same value but different extensions produce different keys.
public func LocalizedWithKeyExtension(_ value: String, _ comment: String, _ keyExtension: String) -> String {
    LocalizedStringKitCore.shared.localize(value: value, comment: comment, keyExtension: keyExtension, bundleName: nil)
}

/// Localize a string with both a key extension and a bundle.
///
/// - Parameters:
///   - value: The English string.
///   - comment: Context describing where the value is used.
///   - keyExtension: Included when generating the key.
///   - bundleName: Optional bundle used to segment groups of strings.
public func LocalizedWithKeyExtensionAndBundle(
    _ value: String,
    _ comment: String,
    _ keyExtension: String,
    _ bundleName: String?
) -> String {
    LocalizedStringKitCore.shared.localize(
        value: value,
        comment: comment,
        keyExtension: keyExtension,
        bundleName: bundleName
    )
}

/// Marks a string as not needing localization (to avoid false positives from
/// the static analyzer / generation tool).
public func LocalizationUnnecessary(_ value: String) -> String {
    value
}

/// Load the bundle which contains the localized strings.
///
/// - Parameter bundleName: Optional bundle name. If `nil`, the primary bundle is used.
public func getLocalizedStringKitBundle(_ bundleName: String?) -> Bundle? {
    LocalizedStringKitCore.shared.bundle(named: bundleName)
}

/// Compute the localization key for a value (and optional key extension).
///
/// The key is the hex-encoded MD5 of the full UTF-8 value, or of
/// `<value>:<keyExtension>` when a non-empty key extension is supplied. This
/// must match the key produced by the generation tool.
public func LSKKeyForValue(_ value: String, _ keyExtension: String?) -> String {
    LocalizedStringKitCore.key(value: value, keyExtension: keyExtension)
}

/// Set the primary bundle name.
public func LSKSetPrimaryBundleName(_ bundleName: String) {
    LSKPrimaryBundleName = bundleName
}

/// Set the alternate bundle search path.
public func LSKSetAlternateBundleSearchPath(_ url: URL) {
    LSKAlternateBundleSearchPath = url
}

// MARK: - Objective-C compatibility

/// Objective-C facing entry point for LocalizedStringKit.
///
/// Swift callers should prefer the free functions above (`Localized(_:_:)` and
/// friends). Objective-C callers use these class methods, e.g.
/// `[LSKLocalizer localized:@"Cancel" comment:@"Action title"]`.
@objc(LSKLocalizer)
public final class LSKLocalizer: NSObject {

    /// The name to be used for the primary strings bundle.
    @objc public class var primaryBundleName: String {
        get { LSKPrimaryBundleName }
        set { LSKPrimaryBundleName = newValue }
    }

    /// URL for alternate string bundle search.
    @objc public class var alternateBundleSearchPath: URL? {
        get { LSKAlternateBundleSearchPath }
        set { LSKAlternateBundleSearchPath = newValue }
    }

    /// Localize a string. See `Localized(_:_:)`.
    @objc public class func localized(_ value: String, comment: String) -> String {
        Localized(value, comment)
    }

    /// Localize a string in a specific bundle. See `LocalizedWithBundle(_:_:_:)`.
    @objc public class func localized(_ value: String, comment: String, bundleName: String?) -> String {
        LocalizedStringKitCore.shared.localize(
            value: value,
            comment: comment,
            keyExtension: nil,
            bundleName: bundleName
        )
    }

    /// Localize a string with a key extension. See
    /// `LocalizedWithKeyExtension(_:_:_:)`.
    @objc public class func localized(_ value: String, comment: String, keyExtension: String?) -> String {
        LocalizedStringKitCore.shared.localize(
            value: value,
            comment: comment,
            keyExtension: keyExtension,
            bundleName: nil
        )
    }

    /// Localize a string with a key extension and optional bundle.
    /// See `LocalizedWithKeyExtensionAndBundle(_:_:_:_:)`.
    @objc public class func localized(
        _ value: String,
        comment: String,
        keyExtension: String?,
        bundleName: String?
    ) -> String {
        LocalizedStringKitCore.shared.localize(
            value: value,
            comment: comment,
            keyExtension: keyExtension,
            bundleName: bundleName
        )
    }

    /// Marks a string as not needing localization.
    @objc public class func localizationUnnecessary(_ value: String) -> String {
        value
    }

    /// Compute the localization key for a value (and optional key extension).
    @objc public class func key(forValue value: String, keyExtension: String?) -> String {
        LocalizedStringKitCore.key(value: value, keyExtension: keyExtension)
    }

    /// Load the bundle which contains the localized strings.
    @objc public class func bundle(named bundleName: String?) -> Bundle? {
        LocalizedStringKitCore.shared.bundle(named: bundleName)
    }
}
