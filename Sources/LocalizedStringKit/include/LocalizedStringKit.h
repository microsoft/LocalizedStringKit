//
//  Copyright (c) Microsoft Corporation. All rights reserved.
//

@import Foundation;

NS_ASSUME_NONNULL_BEGIN

//! Project version number for LocalizedStringKit.
FOUNDATION_EXPORT double LocalizedStringKitVersionNumber;

//! Project version string for LocalizedStringKit.
FOUNDATION_EXPORT const unsigned char LocalizedStringKitVersionString[];

/// Primary localization function used to localize strings
///
/// The `value` should be the English string and the `comment` should give context on where the string is used.
/// Ex: `Localized("Cancel", "Action sheet action title")
NSString *Localized(NSString *value, NSString *comment);

/// Additional localization function used to localize strings
///
/// The `value` should be the English string, the `comment` should give context on where the string is used, and the `keyExtension` should
/// be used to provide additional differentiation between contexts. The `keyExtension` is included when generating the string `key` so two
/// calls with the same `value` but different `keyExtension` values will result in two different strings in the localization dictionary.
///
/// Ex: `LocalizedWithKeyExtension("Archive", "Button title", "Archive action")
/// Ex: `LocalizedWithKeyExtension("Archive", "Folder title", "Archive folder")
NSString *LocalizedWithKeyExtension(NSString *value, NSString *comment, NSString *keyExtension);

/// Marks a string as not needing localization (to avoid false positives from
/// the static analyzer
NSString *LocalizationUnnecessary(NSString *value);

/// Load the bundle which contains the localized strings
NSBundle * _Nullable getLocalizedStringKitBundle(void);

NS_ASSUME_NONNULL_END
