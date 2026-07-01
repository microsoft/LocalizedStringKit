//
//  Copyright (c) Microsoft Corporation. All rights reserved.
//

@import CommonCrypto;
#import <os/lock.h>

#import "LocalizedStringKit.h"

@interface LocalizedStringKit : NSObject

@end

@implementation LocalizedStringKit

static NSMutableDictionary *bundleMap = nil;

// Guards all access to `bundleMap`. `dispatch_once` only guards initialization,
// not the subsequent reads/mutations, so concurrent `Localized()` calls would
// otherwise race on the dictionary.
static os_unfair_lock bundleMapLock = OS_UNFAIR_LOCK_INIT;

#pragma mark - Public

NSString *_Nonnull LSKPrimaryBundleName = @"LocalizedStringKit.bundle";

NSURL *_Nullable LSKAlternateBundleSearchPath = nil;

NSString *Localized(NSString *_Nonnull value, NSString *_Nonnull comment) {
  return [LocalizedStringKit localizeWithValue:value comment:comment keyExtension:nil bundleName:nil];
}

NSString *LocalizedWithBundle(NSString *_Nonnull value, NSString *_Nonnull comment, NSString *_Nonnull bundleName) {
  return [LocalizedStringKit localizeWithValue:value comment:comment keyExtension:nil bundleName:bundleName];
}

NSString *LocalizedWithKeyExtension(NSString *_Nonnull value, NSString *_Nonnull comment, NSString *_Nonnull keyExtension) {
  return [LocalizedStringKit localizeWithValue:value comment:comment keyExtension:keyExtension bundleName:nil];
}

NSString *LocalizedWithKeyExtensionAndBundle(NSString *_Nonnull value, NSString *_Nonnull comment, NSString *_Nonnull keyExtension, NSString *_Nullable bundleName) {
    return [LocalizedStringKit localizeWithValue:value comment:comment keyExtension:keyExtension bundleName:bundleName];
}

__attribute__((annotate("returns_localized_nsstring")))
NSString *LocalizationUnnecessary(NSString *value) {
  return value;
}

NSBundle * _Nullable getLocalizedStringKitBundle(NSString *_Nullable bundleName) {
  return [LocalizedStringKit getLocalizedStringKitBundle:bundleName];
}

NSString *_Nonnull LSKKeyForValue(NSString *_Nonnull value, NSString *_Nullable keyExtension) {
  return [LocalizedStringKit keyWithValue:value keyExtension:keyExtension];
}

#pragma mark - Private / Static

+ (NSString *)localizeWithValue:(NSString *_Nonnull)value comment:(NSString *_Nonnull)comment keyExtension:(NSString *_Nullable)keyExtension bundleName:(NSString *_Nullable)bundleName
{
  // Key
  NSString *key = [self keyWithValue:value keyExtension:keyExtension];

  // Table: This does not change between bundles
  NSString *table = @"LocalizedStringKit";

  // Bundle Map: [bundleName String: NSBundle]
  static dispatch_once_t onceToken;
  dispatch_once(&onceToken, ^{
    bundleMap = [[NSMutableDictionary alloc] init];
  });

  if (bundleName == nil)
  {
    // Default to primary strings bundle
    bundleName = LSKPrimaryBundleName;
  }

  NSBundle *bundle = nil;

  os_unfair_lock_lock(&bundleMapLock);

  bundle = [bundleMap objectForKey:bundleName];

  if (bundle == nil)
  {
    // Load and cache bundle
    bundle = [LocalizedStringKit getLocalizedStringKitBundle:bundleName];
    if (bundle == nil)
    {
      [bundleMap setObject:[NSNull null] forKey:bundleName];
      // Unable to load `LocalizedStringKit` bundle
      os_unfair_lock_unlock(&bundleMapLock);
      return value;
    }
    [bundleMap setObject:bundle forKey:bundleName];
  }

  os_unfair_lock_unlock(&bundleMapLock);

  if ([bundle isKindOfClass:[NSNull class]]) {
    // Resolved NSNull for bundle
    return value;
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

  // Hash the full UTF-8 byte length of the string. Note: `sizeof inputCharacterArray`
  // is the size of the pointer (8 bytes on 64-bit), not the string length, so it must
  // not be used to bound the hash input or the key would only cover the first 8 bytes.
  // This must stay in sync with the generator, which hashes the full string.
  CC_MD5(inputCharacterArray, (CC_LONG)[hashInput lengthOfBytesUsingEncoding:NSUTF8StringEncoding], outputCharacterArray);

  NSMutableString *key = [[NSMutableString alloc] init];

  for (NSInteger idx = 0; idx < CC_MD5_DIGEST_LENGTH; idx++) {
    [key appendFormat:@"%02x", outputCharacterArray[idx]];
  }

  return key;
}

+ (NSBundle *_Nullable)getLocalizedStringKitBundle:(NSString *_Nullable)bundleName
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

    if (bundle != nil)
    {
      if ([bundle.bundleURL.lastPathComponent isEqualToString:bundleName]) {
        return bundle;
      }
      else {
        break;
      }
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

void LSKSetAlternateBundleSearchPath(NSURL *_Nonnull url) {
  LSKAlternateBundleSearchPath = url;
  os_unfair_lock_lock(&bundleMapLock);
  [bundleMap removeAllObjects];
  os_unfair_lock_unlock(&bundleMapLock);
}

@end
