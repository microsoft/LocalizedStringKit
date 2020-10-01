// 1. Should localize with key extension
LocalizedWithKeyExtension(@"Value", @"Comment", @"Key Extension");

// 2. Should localize with `value` and `comment`
Localized(@"Calendar", @"The name of the calendar tab.");

// 3. Should localize with `value` and empty `comment`
Localized(@"Email", @"Some email label");

// 4. + 5. Should localize successive calls in a single line
detailItems.append(WhatsNewDetailItem(title: Localized(@"Apple Watch App", @"The title of the what's new content for the new Apple Watch support."), body: Localized(@"Clear through out Outlook inbox or calendar just by swiping up from the Watch face.", @"The body of the what's new content for the new Apple Watch support")));

// 6. Should localize with quotes in `value`
Localized(@"Send invitation to \"%@\"?", @"Prompt whether or not to send an invitation for event with subject name.");

// 7. Should localize with tricky `value` that looks like the end of the first parameter
Localized(@"Some string with a tricky \", @\" first parameter.", @"Comment");

// 8. Should localize with tricky `comment` that looks like the end of the second parameter
Localized(@"People", @"Comment containing \") but the sentence continues.");

// 9. Should localize with minimal spacing format
Localized(@"Settings",@"The name of the settings tab.");

// 10. Should localize with multi-line spacing format
Localized(
  @"Files",
  @"The name of the files tab."
);

// 11. Should localize with unrealistic multi-line spacing format
Localized(

      @"Close",
                   @"The name of the close menu button."


);

// 12. Should localize with special tokens in `value` and `comment`
Localized(@"First special token: \n and second special token: \"", @"This value contains some special tokens.");

// 13. Should localize with `value`, `comment`, and `bundle`
LocalizedWithBundle(@"Another value", @"Some comment", @"info.bundle")

// 14. Should localize with `value`, `comment`, `key_extension` and `bundle`
LocalizedWithKeyExtensionAndBundle(@"Another value", @"Some comment", @"Verb", @"info.bundle")