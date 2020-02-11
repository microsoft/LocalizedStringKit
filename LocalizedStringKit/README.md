# LocalizedStringKit.framework

This framework provides a simplified API for localized strings and can be attached to all targets that need string localization.

```swift
public func Localized(value: String, _ comment: String) -> String

// ...

let label = UILabel()
label.text = Localized("Mail", "The label text for the Mail tab.")
```

```objc
NSString *Localized(NSString *value, NSString *comment);

// ...

UILabel *label = [[UILabel alloc] init]
label.text = Localized(@"Mail", @"The label text for the Mail tab.")
```

...

```bash
./LocalizedStringKit/localize.py

git commit -a -m "Add localized label text for the Mail tab label"
```

## `localize.py`

This script processes all of the source files (`*.swift` and `*.m`) for occurrences of the `Localized` function and translates them to `NSLocalizedString` function calls. Then the output is passed to `genstrings` to generate an updated `LocalizedStringKit/en.lproj/LocalizedStringKit.strings` file.

The script currently searches these directories:

- `app-ios`
- `ComposeShareExtension`
- `app-ios WatchKit App`
- `app-ios WatchKit Extension`
- `app-ios WatchOS App`
- `app-ios WatchOS App Extension`
- `OutlookUI`
- `AcompliKit`
