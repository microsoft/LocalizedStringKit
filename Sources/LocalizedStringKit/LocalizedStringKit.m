//
//  Copyright (c) Microsoft Corporation. All rights reserved.
//

@import Foundation;

#import "LocalizedStringKit.h"

// The implementation lives in Swift (`LSKLocalizer`). When this file is built
// as part of a mixed Swift/Objective-C module (CocoaPods, or the Xcode
// framework target), the build defines `LSK_MIXED_MODULE` and the Swift half is
// exposed through the generated `-Swift.h` header. Otherwise (Swift Package
// Manager) the Swift implementation is a separate module we import.
#if defined(LSK_MIXED_MODULE)
#if __has_include(<LocalizedStringKit/LocalizedStringKit-Swift.h>)
#import <LocalizedStringKit/LocalizedStringKit-Swift.h>
#else
#import "LocalizedStringKit-Swift.h"
#endif
#else
@import LocalizedStringKitCore;
#endif

#pragma mark - Configuration

NSString *_Nonnull LSKPrimaryBundleName = @"LocalizedStringKit.bundle";

NSURL *_Nullable LSKAlternateBundleSearchPath = nil;

#pragma mark - Public free functions

NSString *Localized(NSString *_Nonnull value, NSString *_Nonnull comment) {
  return [LSKLocalizer localizeValue:value
                            comment:comment
                       keyExtension:nil
                         bundleName:LSKPrimaryBundleName
                alternateSearchPath:LSKAlternateBundleSearchPath];
}

NSString *LocalizedWithBundle(NSString *_Nonnull value, NSString *_Nonnull comment, NSString *_Nonnull bundleName) {
  NSString *effectiveBundleName = bundleName ?: LSKPrimaryBundleName;
  return [LSKLocalizer localizeValue:value
                            comment:comment
                       keyExtension:nil
                         bundleName:effectiveBundleName
                alternateSearchPath:LSKAlternateBundleSearchPath];
}

NSString *LocalizedWithKeyExtension(NSString *_Nonnull value, NSString *_Nonnull comment, NSString *_Nonnull keyExtension) {
  return [LSKLocalizer localizeValue:value
                            comment:comment
                       keyExtension:keyExtension
                         bundleName:LSKPrimaryBundleName
                alternateSearchPath:LSKAlternateBundleSearchPath];
}

NSString *LocalizedWithKeyExtensionAndBundle(NSString *_Nonnull value, NSString *_Nonnull comment, NSString *_Nonnull keyExtension, NSString *_Nullable bundleName) {
  NSString *effectiveBundleName = bundleName ?: LSKPrimaryBundleName;
  return [LSKLocalizer localizeValue:value
                            comment:comment
                       keyExtension:keyExtension
                         bundleName:effectiveBundleName
                alternateSearchPath:LSKAlternateBundleSearchPath];
}

__attribute__((annotate("returns_localized_nsstring")))
NSString *LocalizationUnnecessary(NSString *value) {
  return value;
}

NSBundle *_Nullable getLocalizedStringKitBundle(NSString *_Nullable bundleName) {
  NSString *effectiveBundleName = bundleName ?: LSKPrimaryBundleName;
  return [LSKLocalizer bundleForName:effectiveBundleName alternateSearchPath:LSKAlternateBundleSearchPath];
}

NSBundle *_Nullable LSKLocalizedStringKitBundle(NSString *_Nullable bundleName) {
  return getLocalizedStringKitBundle(bundleName);
}

NSString *_Nonnull LSKKeyForValue(NSString *_Nonnull value, NSString *_Nullable keyExtension) {
  return [LSKLocalizer keyForValue:value keyExtension:keyExtension];
}

void LSKSetPrimaryBundleName(NSString *_Nonnull bundleName) {
  LSKPrimaryBundleName = bundleName;
}

void LSKSetAlternateBundleSearchPath(NSURL *_Nonnull url) {
  LSKAlternateBundleSearchPath = url;
}
