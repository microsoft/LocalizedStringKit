//
//  Copyright (c) Microsoft Corporation. All rights reserved.
//

import CommonCrypto
import Foundation

// MARK: - Bundle resolution

/// Backing implementation for LocalizedStringKit.
///
/// This owns the bundle cache behind a lock so that concurrent `Localized(...)`
/// calls are safe. Configuration (the primary bundle name and the alternate
/// search path) is *not* stored here; it lives in the Objective-C facade and is
/// passed in on each call, matching the historical behavior of the library.
final class BundleResolver {

    /// Shared singleton.
    static let shared = BundleResolver()

    /// The table name is fixed and does not change between bundles.
    private static let table = "LocalizedStringKit"

    /// Guards the caches.
    private let lock = NSLock()

    /// Cache of resolved bundles keyed by bundle name.
    private var bundleCache: [String: Bundle] = [:]

    /// Names we already tried to resolve and failed. Mirrors the original
    /// `NSNull` sentinel so we don't repeatedly hit the filesystem.
    private var knownMissing: Set<String> = []

    /// Localize a value.
    ///
    /// - Parameters:
    ///   - value: The English string.
    ///   - comment: Context for translators.
    ///   - keyExtension: Optional string to differentiate homographs.
    ///   - bundleName: The (already resolved) bundle name to look in.
    ///   - alternateSearchPath: Optional root to search before the main bundle.
    /// - Returns: The localized string, or `value` if no bundle/entry is found.
    func localize(
        value: String,
        comment: String,
        keyExtension: String?,
        bundleName: String,
        alternateSearchPath: URL?
    ) -> String {
        let key = Self.key(value: value, keyExtension: keyExtension)

        lock.lock()

        if knownMissing.contains(bundleName) {
            lock.unlock()
            return value
        }

        var bundle = bundleCache[bundleName]

        if bundle == nil {
            bundle = Self.loadBundle(named: bundleName, alternateSearchPath: alternateSearchPath)

            guard let resolved = bundle else {
                knownMissing.insert(bundleName)
                lock.unlock()
                return value
            }

            bundleCache[bundleName] = resolved
        }

        let resolvedBundle = bundle!
        lock.unlock()

        return resolvedBundle.localizedString(forKey: key, value: value, table: Self.table)
    }

    /// Resolve the bundle for the given name, honoring the alternate search path.
    func bundle(named bundleName: String, alternateSearchPath: URL?) -> Bundle? {
        Self.loadBundle(named: bundleName, alternateSearchPath: alternateSearchPath)
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
    private static func loadBundle(named bundleName: String, alternateSearchPath: URL?) -> Bundle? {
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

// MARK: - Objective-C entry point

/// Low-level Objective-C facing entry point for LocalizedStringKit.
///
/// This is the bridge used by the Objective-C facade (`LocalizedStringKit.m`),
/// which exposes the historical C free functions (`Localized(...)` and friends)
/// that both Objective-C and Swift consumers call. Configuration state lives in
/// that facade and is passed in explicitly here.
@objc(LSKLocalizer)
public final class LSKLocalizer: NSObject {

    /// Localize a string.
    @objc(localizeValue:comment:keyExtension:bundleName:alternateSearchPath:)
    public class func localize(
        value: String,
        comment: String,
        keyExtension: String?,
        bundleName: String,
        alternateSearchPath: URL?
    ) -> String {
        BundleResolver.shared.localize(
            value: value,
            comment: comment,
            keyExtension: keyExtension,
            bundleName: bundleName,
            alternateSearchPath: alternateSearchPath
        )
    }

    /// Compute the localization key for a value (and optional key extension).
    @objc(keyForValue:keyExtension:)
    public class func key(forValue value: String, keyExtension: String?) -> String {
        BundleResolver.key(value: value, keyExtension: keyExtension)
    }

    /// Load the bundle which contains the localized strings.
    @objc(bundleForName:alternateSearchPath:)
    public class func bundle(named bundleName: String, alternateSearchPath: URL?) -> Bundle? {
        BundleResolver.shared.bundle(named: bundleName, alternateSearchPath: alternateSearchPath)
    }
}
