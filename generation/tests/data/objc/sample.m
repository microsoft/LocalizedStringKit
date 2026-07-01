// 1. Should localize with key extension
[LSKLocalizer localized:@"Value" comment:@"Comment" keyExtension:@"Key Extension"];

// 2. Should localize with `value` and `comment`
[LSKLocalizer localized:@"Calendar" comment:@"The name of the calendar tab."];

// 3. Should localize with `value` and empty `comment`
[LSKLocalizer localized:@"Email" comment:@"Some email label"];

// 4. + 5. Should localize successive calls in a single line
detailItems.append(WhatsNewDetailItem(title: [LSKLocalizer localized:@"Apple Watch App" comment:@"The title of the what's new content for the new Apple Watch support."], body: [LSKLocalizer localized:@"Clear through out Outlook inbox or calendar just by swiping up from the Watch face." comment:@"The body of the what's new content for the new Apple Watch support"]));

// 6. Should localize with quotes in `value`
[LSKLocalizer localized:@"Send invitation to \"%@\"?" comment:@"Prompt whether or not to send an invitation for event with subject name."];

// 7. Should localize with tricky `value` that looks like the end of the first parameter
[LSKLocalizer localized:@"Some string with a tricky \", @\" first parameter." comment:@"Comment"];

// 8. Should localize with tricky `comment` that looks like the end of the second parameter
[LSKLocalizer localized:@"People" comment:@"Comment containing \") but the sentence continues."];

// 9. Should localize with minimal spacing format
[LSKLocalizer localized:@"Settings" comment:@"The name of the settings tab."];

// 10. Should localize with multi-line spacing format
[LSKLocalizer localized:@"Files"
              comment:@"The name of the files tab."];

// 11. Should localize with unrealistic multi-line spacing format
[LSKLocalizer localized:@"Close"

                   comment:@"The name of the close menu button."


];

// 12. Should localize with special tokens in `value` and `comment`
[LSKLocalizer localized:@"First special token: \n and second special token: \"" comment:@"This value contains some special tokens."];

// 13. Should localize with `value`, `comment`, and `bundle`
[LSKLocalizer localized:@"Another value" comment:@"Some comment" bundleName:@"info.bundle"];

// 14. Should localize with `value`, `comment`, `key_extension` and `bundle`
[LSKLocalizer localized:@"Another value" comment:@"Some comment" keyExtension:@"Verb" bundleName:@"info.bundle"];

[LSKLocalizer localized:@"%#@firstValue@ and %#@secondValue@" comment:@"Some comment"];

[LSKLocalizer localized:@"%#@firstValue@ and %#@secondValue@" comment:@"Some comment" bundleName:@"info.bundle"];
