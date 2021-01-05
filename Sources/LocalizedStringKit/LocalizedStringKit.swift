//
//  Copyright (c) Microsoft Corporation. All rights reserved.
//

import Foundation
import CryptoKit


public func Localized(_ value: String, _ comment: String, keyExtension: String? = nil, bundleName: String? = nil) -> String {
    return Localizer.localize(value, comment, keyExtension: keyExtension, bundleName: bundleName)
}

/// Soft deprecated. Use `Localized(value, comment, keyExtension: keyExtension)` instead
public func LocalizedWithKeyExtension(_ value: String, _ comment: String, _ keyExtension: String) -> String {
    return Localizer.localize(value, comment, keyExtension: keyExtension, bundleName: nil)
}

/// Soft deprecated. Use `Localized(value, comment, bundleName: bundleName)` instead
public func LocalizedWithBundle(_ value: String, _ comment: String, _ bundleName: String) -> String {
    return Localizer.localize(value, comment, keyExtension: nil, bundleName: bundleName)
}

/// Soft deprecated. Use `Localized(value, comment, keyExtension: keyExtension, bundleName: bundleName)` instead
public func LocalizedWithKeyExtensionAndBundle(_ value: String, _ comment: String, _ keyExtension: String, _ bundleName: String) -> String {
    return Localizer.localize(value, comment, keyExtension: keyExtension, bundleName: bundleName)
}

public class Localizer {

    private static var bundleMap = [String: Bundle]()
    private static var missingBundles: Set<String> = Set()
    public static var primaryBundleName = "LocalizedStringKit.bundle"
    public static var alternateBundleSearchPath: URL? {
        didSet {
            bundleMap.removeAll()
        }
    }

    static func md5(string: String) -> String? {
        guard let data = string.data(using: .utf8) else {
            return nil
        }

        let digest = Insecure.MD5.hash(data: data)

        return digest.map { String(format: "%02hhx", $0) }.joined()
    }

    static func key(_ value: String, keyExtension: String?) -> String? {
        // Generate the `key` which is equal to the `MD5(<value>)` or `MD5(<value>:<keyExtension>)`. This logic must stay in sync with `localize.py`.
        var hashInput = value

        if let ke = keyExtension, ke.isEmpty {
            hashInput = hashInput.appendingFormat(":%@", ke)
        }

        return md5(string: hashInput)
    }

    static func getBundle(_ bundleName: String?) -> Bundle? {
        // Search Paths
        var searchPath = Bundle.main.bundleURL

        // Determine target bundleName
        var bundleName = bundleName ?? primaryBundleName

        // Append suffix
        if !bundleName.hasSuffix(".bundle") {
            bundleName += ".bundle"
        }

        // Alternate path check, if url specified
        if let alernateSearchPath = alternateBundleSearchPath,
           let bundle = Bundle(url: alernateSearchPath.appendingPathComponent(bundleName)) {
                return bundle
        }

        // Primary searchPath check
        while true {
            let bundleURL = searchPath.appendingPathComponent(bundleName)
            if let bundle = Bundle(url: bundleURL) {
                if bundle.bundleURL.lastPathComponent == bundleName {
                    return bundle
                } else {
                    break
                }
            }

            let newPath = searchPath.appendingPathComponent("..").absoluteURL
            if newPath == searchPath {
                break
            }

            searchPath = newPath
        }

        return nil
    }

    @objc static func localize(_ value: String, _ comment: String, keyExtension: String?, bundleName: String?) -> String {
        let bundleName = bundleName ?? "LocalizedStringKit.bundle"
        let table = "LocalizedStringKit" // This does not change between bundles

        guard let key = self.key(value, keyExtension: keyExtension) else {
            return value
        }

        if let cachedBundle = bundleMap[bundleName] {
            return NSLocalizedString(key, tableName: table, bundle: cachedBundle, value: value, comment: comment)
        }

        // We can't find it, so don't bother searching again
        guard !missingBundles.contains(bundleName) else {
            return value
        }

        // Bundle wasn't cached so fetch and cache
        guard let bundle = getBundle(bundleName) else {
            missingBundles.insert(bundleName)
            return value
        }

        bundleMap[bundleName] = bundle

        // Forward to `NSLocalizedString`
        return NSLocalizedString(key, tableName: table, bundle: bundle, value: value, comment: comment)
    }

}
