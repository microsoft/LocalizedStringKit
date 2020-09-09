//
//  Copyright (c) Microsoft Corporation. All rights reserved.
//

@import Foundation;

NS_ASSUME_NONNULL_BEGIN

//! Project version number for LocalizedStringKit.
FOUNDATION_EXPORT double LocalizedStringKitVersionNumber;

//! Project version string for LocalizedStringKit.
FOUNDATION_EXPORT const unsigned char LocalizedStringKitVersionString[];

/// Primary localization function used to localize strings (excluding tableName)
///
/// @param value: The English string
/// @param comment: String to give context where the value string is used
///
/// Examples
/// Localized("Cancel", "Action sheet action title")
NSString *Localized(NSString *_Nonnull value, NSString *_Nonnull comment);


/// Primary localization function used to localize strings
///
/// @param value: The English string
/// @param comment: String to give context where the value string is used
/// @param tableName: String to provide additional classification of the value string. Can be used to segment groups of strings in multiple bundles.
///
/// Examples
/// Localized("Cancel", "Action sheet action title", nil)
/// Localized("Cancel", "Action sheet action title", "primary")
/// Localized("Cancel", "Action sheet action title", "primary")
NSString *LocalizedWithTable(NSString *_Nonnull value, NSString *_Nonnull comment, NSString *_Nonnull tableName);

/// Additional localization function used to localize strings
///
/// @param value: The English string
/// @param comment: String to give context where the value string is used
/// @param keyExtension: String to be used to provide additional differentiation between contexts. The `keyExtension` is included when generating the string `key` so two calls with the same `value` but different `keyExtension` values will result in two different strings in the localization dictionary
/// @param tableName: Optional string to provide additional classification of the string. Can be used to segment groups of strings in multiple bundles.
///
/// Ex: `LocalizedWithKeyExtension("Archive", "Button title", "Archive action", nil)
/// Ex: `LocalizedWithKeyExtension("Archive", "Folder title", "Archive folder", nil)
NSString *LocalizedWithKeyExtension(NSString *_Nonnull value, NSString *_Nonnull scomment, NSString *_Nonnull keyExtension, NSString *_Nullable tableName);

/// Marks a string as not needing localization (to avoid false positives from
/// the static analyzer
NSString *LocalizationUnnecessary(NSString *value);

/// Load the bundle which contains the localized strings
///
/// @param tableName: Optional tableName to find related bundle for strings. tableNames can be used to segment localized string bundles. If nil, default bundle will be returned.
NSBundle * _Nullable getLocalizedStringKitBundle(NSString *_Nullable tableName);

NS_ASSUME_NONNULL_END
