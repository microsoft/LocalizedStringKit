//
//  Copyright (c) Microsoft Corporation. All rights reserved.
//

@import CommonCrypto;

#import "LocalizedStringKit.h"

@interface LocalizedStringKit : NSObject

@end

@implementation LocalizedStringKit

#pragma mark - Public

NSString *Localized(NSString *_Nonnull value, NSString *_Nonnull comment, NSString *_Nullable tableName) {
  return [LocalizedStringKit localizeWithValue:value comment:comment keyExtension:nil tableName:tableName];
}

NSString *LocalizedWithKeyExtension(NSString *_Nonnull value, NSString *_Nonnull comment, NSString *_Nonnull keyExtension, NSString *_Nullable tableName) {
  return [LocalizedStringKit localizeWithValue:value comment:comment keyExtension:keyExtension tableName:tableName];
}

__attribute__((annotate("returns_localized_nsstring")))
NSString *LocalizationUnnecessary(NSString *value) {
  return value;
}

NSBundle *getLocalizedStringKitBundle(NSString *_Nullable tableName) {
  return [LocalizedStringKit getLocalizedStringKitBundle:tableName];
}

#pragma mark - Private / Static

+ (NSString *)localizeWithValue:(NSString *_Nonnull)value comment:(NSString *_Nonnull)comment keyExtension:(NSString *_Nullable)keyExtension tableName:(NSString *_Nullable)tableName
{
  // Key
  NSString *key = [self keyWithValue:value keyExtension:keyExtension];

  // Table: This does not change between bundles
  NSString *table = @"LocalizedStringKit";

  // Bundle Map: [tableName String: NSBundle]
  static NSMutableDictionary<NSString *, NSBundle *> *bundleMap = nil;
  static dispatch_once_t onceToken;
  dispatch_once(&onceToken, ^{
    bundleMap = [[NSMutableDictionary alloc] init];
  });

  if (tableName == nil)
  {
    // Default to primary strings bundle
    tableName = @"LocalizedStringKit.bundle";
  }

  NSBundle *bundle = [bundleMap objectForKey:tableName];

  if (bundle == nil)
  {
    // Load and cache bundle
    bundle = [LocalizedStringKit getLocalizedStringKitBundle:tableName];
    [bundleMap setObject:bundle forKey:tableName];
  }

  if (bundle == nil)
  {
    // Unable to load `LocalizedStringKit` bundle
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

  CC_MD5(inputCharacterArray, (CC_LONG)strlen(inputCharacterArray), outputCharacterArray);

  NSMutableString *key = [[NSMutableString alloc] init];

  for (NSInteger idx = 0; idx < CC_MD5_DIGEST_LENGTH; idx++) {
    [key appendFormat:@"%02x", outputCharacterArray[idx]];
  }

  return key;
}

+ (NSBundle *)getLocalizedStringKitBundle:(NSString *_Nullable)tableName
{
  NSURL *searchPath = [[NSBundle mainBundle] bundleURL];

  if (tableName == nil) {
    // Defaults to primary bundle if tableName not specified
    tableName = @"LocalizedStringKit.bundle";
  }
  else {
    // Append suffix
    tableName = [tableName stringByAppendingFormat:@".bundle"];
  }

  while(YES)
  {
    NSURL *bundleURL = [searchPath URLByAppendingPathComponent:tableName];
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

@end
