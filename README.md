# LocalizedStringKit

LocalizedStringKit is a tool that lets you write English strings directly into your source code and generate the required .strings files later. No more manually managing string keys or remembering to add them to the strings file later. All you do is change: 

```swift
label.text = NSLocalizedString("TERMS_SCREEN_MAIN_HEADER", "Comment here...")
```

into:

```swift
label.text = Localized("Terms and Conditions", "Comment here...")
```

And you are good to go. 

## Getting started

### Application Library

The app side of the tool is powered by the LocalizedStringKit library. This is a framework which can be easily added to your app via Carthage. Add this repo to your cart file, then link in the library with wherever you need to use it.

### Strings bundle

The app and the library need to be able to access the strings bundle. To do this we are going to do some basic setup:

1. Create a folder in your app project somewhere named `LocalizedStringKit`.
2. Inside that folder, create a new folder named `LocalizedStringKit.bundle` (this will turn it into a bundle).
3. Add this bundle to your project in Xcode
4. Ensure that this bundle is copied to your main app bundle (even if you are going to be using it in a framework).

The disk structure will now look something like:

```
ProjectName/
├── LocalizedStringKit/
|   ├── LocalizedStringKit.bundle/
```

### Creating some new strings

In your source code, add some code like:

```swift
label.text = LocalizedString("My new string", "A comment")
```

Remember to `import LocalizedStringKit` in the file too.

### Generate your strings

Now everything is in place to generate the `.strings` files. For this, you'll need the tool we use to generate the strings files. This exists in the feed here: <https://office.visualstudio.com/Outlook%20Mobile/_packaging?_a=package&feed=olm-shared&package=localizedstringkit&protocolType=PyPI> If you are unfamiliar with installation, there is guidance on the feed page.

Once the tool is installed, you just need to run `generate_localizedstringkit -h` and it will show you how to call it. Here's an example:

```bash
generate_localizedstringkit \
--path /path/to/my/project/root \
--localized-string-kit-path /path/to/my/project/root/LocalizedStringKit
```

This will scan `/path/to/my/project/root/` for all Swift and Objective-C files, extract any calls to `Localized` and generate the `en.lproj/LocalizedStringKit.strings` file. It will also generate a `source_strings.m` file as an intermediate step. This file is kept around as it allows the `generate_localizedstringkit --check` command to be run quickly. You can add it to your `.gitignore` if preferred.


And that's it. You are now up and running with LocalizedStringKit.

## FAQ

### How can I make this tool faster?
We know that this tool is a little slow. Unfortunately there's little we can do to speed it up. Instead, what we have developed is a `--check` flag which can be used. If `source_strings.m` exists in the repo, it will compare the state of the repo to that file, and return a non-zero exit code if there are differences. If that file does not exist, the check flag will always return a non-zero exit code.

### Can this be consumed as a library?
Yes, absolutely. Just `import localizedstringkit`.

### How to migrate existing strings
There is no built in method to migrate existing strings, but it's relatively straightforward to do so. Follow the setup steps above first. Then convert all `NSLocalizedString` calls to `Localized` calls, replacing your manual key with the English string. Then run the generate script mentioned above.


# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.