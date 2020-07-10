//
//  Copyright (c) Microsoft Corporation. All rights reserved.
//

@import CommonCrypto;

#import "LocalizedStringKit.h"

@interface LocalizedStringKit : NSObject

@end

@implementation LocalizedStringKit

NSString *Localized(NSString *value, NSString *comment) {
  return [LocalizedStringKit localizeWithValue:value comment:comment keyExtension:nil];
}

NSString *LocalizedWithKeyExtension(NSString *value, NSString *comment, NSString *keyExtension) {
  return [LocalizedStringKit localizeWithValue:value comment:comment keyExtension:keyExtension];
}

__attribute__((annotate("returns_localized_nsstring")))
NSString *LocalizationUnnecessary(NSString *value) {
  return value;
}

NSBundle *getLocalizedStringKitBundle() {
  return [LocalizedStringKit getLocalizedStringKitBundle];
}

+ (NSString *)localizeWithValue:(NSString *)value comment:(NSString *)comment keyExtension:(NSString *)keyExtension
{
  // Key
  NSString *key = [self keyWithValue:value keyExtension:keyExtension];

  // Table
  NSString *table = @"LocalizedStringKit";

  // Bundle
  static NSBundle *bundle = nil;

  if (bundle == nil)
  {
    // Load cached reference ot `LocalizedStringKit` bundle
    bundle = [LocalizedStringKit getLocalizedStringKitBundle];
  }

  if (bundle == nil)
  {
    // Unable to load `LocalizedStringKit` bundle
    return value;
  }

  // Forward to `NSLocalizedString`
  return NSLocalizedStringWithDefaultValue(key, table, bundle, value, comment);
}

+ (NSString *)keyWithValue:(NSString *)value keyExtension:(NSString *)keyExtension
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

+ (NSBundle *)getLocalizedStringKitBundle
{
  NSURL *searchPath = [[NSBundle mainBundle] bundleURL];

  while(YES)
  {
    NSURL *bundleURL = [searchPath URLByAppendingPathComponent:@"LocalizedStringKit.bundle"];
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
