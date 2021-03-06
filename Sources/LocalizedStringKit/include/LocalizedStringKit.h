//
//  Copyright (c) Microsoft Corporation. All rights reserved.
//

@import Foundation;

NS_ASSUME_NONNULL_BEGIN

//! Project version number for LocalizedStringKit.
FOUNDATION_EXPORT double LocalizedStringKitVersionNumber;

//! Project version string for LocalizedStringKit.
FOUNDATION_EXPORT const unsigned char LocalizedStringKitVersionString[];

/// The name to be used for the primary strings bundle
/// Example:
/// "Localizable" (do not include the extension suffix)
FOUNDATION_EXPORT NSString *_Nonnull LSKPrimaryBundleName;

/// URL for alternate string bundle search (the root from where search will begin)
FOUNDATION_EXPORT NSURL *_Nullable LSKAlternateBundleSearchPath;

/// Primary localization function used to localize strings (excluding bundleName)
///
/// @param value The English string
/// @param comment String to give context where the value string is used
///
/// Examples
/// Localized("Cancel", "Action sheet action title")
NSString *Localized(NSString *_Nonnull value, NSString *_Nonnull comment);

/// Primary localization function used to localize strings
///
/// @param value The English string
/// @param comment String to give context where the value string is used
/// @param bundleName String to provide additional classification of the value string. Can be used to segment groups of strings in multiple bundles.
///
/// Examples
/// Localized("Cancel", "Action sheet action title", nil)
/// Localized("Cancel", "Action sheet action title", "primary")
/// Localized("Cancel", "Action sheet action title", "primary")
NSString *LocalizedWithBundle(NSString *_Nonnull value, NSString *_Nonnull comment, NSString *_Nonnull bundleName);

/// Additional localization function used to localize strings
///
/// @param value The English string
/// @param comment String to give context where the value string is used
/// @param keyExtension String to be used to provide additional differentiation between contexts. The `keyExtension` is included when generating the string `key` so two calls with the same `value` but different `keyExtension` values will result in two different strings in the localization dictionary
///
/// Ex: `LocalizedWithKeyExtension("Archive", "Button title", "Verb")
/// Ex: `LocalizedWithKeyExtension("Archive", "Folder title", "Noun")
NSString *LocalizedWithKeyExtension(NSString *_Nonnull value, NSString *_Nonnull comment, NSString *_Nonnull keyExtension);

/// Additional localization function used to localize strings
///
/// @param value The English string
/// @param comment String to give context where the value string is used
/// @param keyExtension String to be used to provide additional differentiation between contexts. The `keyExtension` is included when generating the string `key` so two calls with the same `value` but different `keyExtension` values will result in two different strings in the localization dictionary
/// @param bundleName Optional string to provide additional classification of the string. Can be used to segment groups of strings in multiple bundles.
///
/// Ex: `LocalizedWithKeyExtensionAndBundle("Archive", "Button title", "Verb", "primary")
/// Ex: `LocalizedWithKeyExtensionAndBundle("Archive", "Folder title", "Noun", "primary")
NSString *LocalizedWithKeyExtensionAndBundle(NSString *_Nonnull value, NSString *_Nonnull comment, NSString *_Nonnull keyExtension, NSString *_Nullable bundleName);

/// Marks a string as not needing localization (to avoid false positives from
/// the static analyzer
NSString *LocalizationUnnecessary(NSString *value);

/// Load the bundle which contains the localized strings
///
/// @param bundleName Optional bundleName to find related bundle for strings. bundleNames can be used to segment localized string bundles. If nil, default bundle will be returned.
NSBundle * _Nullable LSKLocalizedStringKitBundle(NSString *_Nullable bundleName);

/// Set the primary bundle name
///
/// @param bundleName Nonnull bundle name to set as a String
void LSKSetPrimaryBundleName(NSString *_Nonnull bundleName);

/// Set the alternate bundle search path
///
/// @param url URL to search
void LSKSetAlternateBundleSearchPath(NSURL *_Nonnull url);

/// Get a strings bundle
///
/// @param bundleName Name of bundle to search for
NSBundle * _Nullable getLocalizedStringKitBundle(NSString *_Nullable bundleName);

NS_ASSUME_NONNULL_END
