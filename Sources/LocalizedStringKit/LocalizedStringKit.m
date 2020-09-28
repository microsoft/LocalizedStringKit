//
//  Copyright (c) Microsoft Corporation. All rights reserved.
//

@import CommonCrypto;

#import "LocalizedStringKit.h"

@interface LocalizedStringKit : NSObject

@end

@implementation LocalizedStringKit

#pragma mark - Public

NSString *_Nonnull LSKPrimaryBundleName = @"LocalizedStringKit.bundle";

NSURL *_Nullable LSKAlternateBundleSearchPath = nil;

NSString *Localized(NSString *_Nonnull value, NSString *_Nonnull comment) {
  return [LocalizedStringKit localizeWithValue:value comment:comment keyExtension:nil bundleName:nil];
}

NSString *LocalizedWithBundle(NSString *_Nonnull value, NSString *_Nonnull comment, NSString *_Nonnull bundleName) {
  return [LocalizedStringKit localizeWithValue:value comment:comment keyExtension:nil bundleName:bundleName];
}

NSString *LocalizedWithKeyExtension(NSString *_Nonnull value, NSString *_Nonnull comment, NSString *_Nonnull keyExtension, NSString *_Nullable bundleName) {
  return [LocalizedStringKit localizeWithValue:value comment:comment keyExtension:keyExtension bundleName:bundleName];
}

__attribute__((annotate("returns_localized_nsstring")))
NSString *LocalizationUnnecessary(NSString *value) {
  return value;
}

NSBundle *getLocalizedStringKitBundle(NSString *_Nullable bundleName) {
  return [LocalizedStringKit getLocalizedStringKitBundle:bundleName];
}

#pragma mark - Private / Static

+ (NSString *)localizeWithValue:(NSString *_Nonnull)value comment:(NSString *_Nonnull)comment keyExtension:(NSString *_Nullable)keyExtension bundleName:(NSString *_Nullable)bundleName
{
  // Key
  NSString *key = [self keyWithValue:value keyExtension:keyExtension];

  // Table: This does not change between bundles
  NSString *table = @"LocalizedStringKit";

  // Bundle Map: [bundleName String: NSBundle]
  static NSMutableDictionary<NSString *, NSBundle *> *bundleMap = nil;
  static dispatch_once_t onceToken;
  dispatch_once(&onceToken, ^{
    bundleMap = [[NSMutableDictionary alloc] init];
  });

  if (bundleName == nil)
  {
    // Default to primary strings bundle
    bundleName = @"LocalizedStringKit.bundle";
  }

  NSBundle *bundle = [bundleMap objectForKey:bundleName];

  if (bundle == nil)
  {
    // Load and cache bundle
    bundle = [LocalizedStringKit getLocalizedStringKitBundle:bundleName];
    if (bundle == nil)
    {
      // Unable to load `LocalizedStringKit` bundle
      return value;
    }
    [bundleMap setObject:bundle forKey:bundleName];
  }

  // Forward to `NSLocalizedString`
  return NSLocalizedStringWithDefaultValue(key, table, bundle, value, comment);
}

+ (NSString *)keyWithValue:(NSString *_Nonnull)value keyExtension:(NSString *)keyExtension
{
  // Generate the `key` which is equal to the `MD5(<value>)` or `MD5(<value>:<keyExtension>)`. This logic must stay in sync with `localize.py`.
  NSString *hashInput = value;

  if (keyExtension.length > 0)
  {
    hashInput = [hashInput stringByAppendingFormat:@":%@", keyExtension];
  }

  const char *inputCharacterArray = [hashInput UTF8String];
  unsigned char outputCharacterArray[CC_MD5_DIGEST_LENGTH];

  CC_MD5(inputCharacterArray, (CC_LONG)strlen(inputCharacterArray), outputCharacterArray);

  NSMutableString *key = [[NSMutableString alloc] init];

  for (NSInteger idx = 0; idx < CC_MD5_DIGEST_LENGTH; idx++) {
    [key appendFormat:@"%02x", outputCharacterArray[idx]];
  }

  return key;
}

+ (NSBundle *)getLocalizedStringKitBundle:(NSString *_Nullable)bundleName
{
  // Search Paths
  NSURL *searchPath = [[NSBundle mainBundle] bundleURL];

  // Determine target bundleName
  if (bundleName == nil) {
    // Defaults to primary bundle if bundleName not specified
    bundleName = LSKPrimaryBundleName;
  }
  else if (![bundleName hasSuffix:@".bundle"])
  {
    // Append suffix
    bundleName = [bundleName stringByAppendingFormat:@".bundle"];
  }

  // Alternate path check, if url specified
  if (LSKAlternateBundleSearchPath != nil) {
    NSURL *alternateBundleURL = [LSKAlternateBundleSearchPath URLByAppendingPathComponent:bundleName];
    NSBundle *bundle = [NSBundle bundleWithURL:alternateBundleURL];
    if (bundle) {
      return bundle;
    }
  }

  // Primary searchPath check
  while(YES)
  {
    NSURL *bundleURL = [searchPath URLByAppendingPathComponent:bundleName];
    NSBundle *bundle = [NSBundle bundleWithURL:bundleURL];

    if (bundle)
    {
      return bundle;
    }

    NSURL *newPath = [[searchPath URLByAppendingPathComponent:@".."] absoluteURL];
    if ([newPath isEqual:searchPath])
    {
      break;
    }

    searchPath = newPath;
  }

  return nil;
}

void LSKSetPrimaryBundleName(NSString *_Nonnull bundleName) {
  LSKPrimaryBundleName = bundleName;
}

@end
