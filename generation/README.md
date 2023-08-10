# LocalizedStringKit

[![PyPi Version](https://img.shields.io/pypi/v/LocalizedStringKit.svg)](https://pypi.org/project/LocalizedStringKit/)
[![License](https://img.shields.io/pypi/l/LocalizedStringKit.svg)](https://github.com/Microsoft/LocalizedStringKit/blob/master/LICENSE)
![LocalizedStringKit Logo](https://raw.githubusercontent.com/microsoft/localizedStringKit/master/logo.png)

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

The app side of the tool is powered by the LocalizedStringKit library.

The recommended way of consuming this library is via [Carthage](https://github.com/Carthage/Carthage). The line to add to your `Cartfile` is: `github "Microsoft/localizedstringkit"`

For any issues, refer to the Carthage documentation.

### Strings bundle

The app and the library need to be able to access the strings bundle(s). To do this we are going to do some basic setup:

#### Primary Bundle

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

#### Secondary Bundle(s): bundleNames

To leverage the bundleName segmentation of strings in multiple bundles, you'll need to create these bundles as well.

1. Navigate to the first `LocalizedStringKit` folder that was created in the Primary set up.
2. Inside that folder, create a new folder named `<bundleName>.bundle` (this will turn it into a bundle). Make sure to replace `bundleName` with the case sensitive bundleName you will use in your source.
3. Add this bundle to your project in Xcode
4. Ensure that this bundle is copied to your main app bundle (even if you are going to be using it in a framework).

### Creating some new strings

In your source code, add some code like:

```swift
label.text = Localized("My new string", "A comment")
```

Remember to `import LocalizedStringKit` in the file too.

### Generate your strings

Now everything is in place to generate the `.strings` files. For this, you'll need the tool we use to generate the strings files. It is a Python tool and can be installed by running `pip install localizedstringkit`.

Once the tool is installed, you just need to run `localizedstringkit -h` and it will show you how to call it. Here's an example:

```bash
localizedstringkit \
--path /path/to/my/project/root \
--localized-string-kit-path /path/to/my/project/root/LocalizedStringKit
```

This will scan `/path/to/my/project/root/` for all Swift and Objective-C files, extract any calls to `Localized` and generate the `en.lproj/LocalizedStringKit.strings` file. It will also generate a `source_strings.m` file as an intermediate step. This file is kept around as it allows the `localizedstringkit --check` command to be run quickly. You can add it to your `.gitignore` if preferred.

And that's it. You are now up and running with LocalizedStringKit.

_Note: Remember that if you use Carthage for installation, you'll need to add `--exclude Carthage` (or whatever your path is) to the command to avoid the library itself being flagged._

## FAQ

### How can I make this tool faster?
We know that this tool is a little slow. Unfortunately there's little we can do to speed it up. Instead, what we have developed is a `--check` flag which can be used. If `source_strings.m` exists in the repo, it will compare the state of the repo to that file, and return a non-zero exit code if there are differences. If that file does not exist, the check flag will always return a non-zero exit code.

### Can this be consumed as a library?
Yes, absolutely. Just `import localizedstringkit`.

### How do I migrate existing strings?
There is no built in method to migrate existing strings, but it's relatively straightforward to do so. Follow the setup steps above first. Then convert all `NSLocalizedString` calls to `Localized` calls, replacing your manual key with the English string. Then run the generate script mentioned above. You'll then need to move your translations through a similar process.

### How are collisions handled?
If you have two strings that are identical then they'll be "merged". By that, they'll share the same key, but the comments will be appended. The result will look something like this in the LocalizedStringKit.strings file:

```
/* Text on button which when tapped will send an email message to a user
   Text on button which when tapped will send a message to the support team */
"1432f32780bbd9cde496343b060fd75d" = "Send Message";
```

However, there will be cases where you don't want this to happen. For example, you may have the word `Schedule` appear as a heading for a screen which show's a users daily schedule, but is also a button which you can press to schedule a meeting. In one case the word is a noun and the other a verb. These will often be different words in other languages, so you want to ensure that they get unique translations. For this, you can use key extensions. For example:

```swift
// Heading
title.text = LocalizedWithKeyExtension("Schedule", "Title for a screen which shows the users daily schedule", "Noun")

// Button
button.text = LocalizedWithKeyExtension("Schedule", "Text for a button which will schedule the meeting currently displayed on screen.", "Verb")
```

In this case the English string and the extension (in this case `Verb` or `Noun`) will be concatenated before hashing to generate the key, resulting in these two cases having different keys. The key extension can be any string you like.

### Why is my app bigger after doing this?

By default, `.strings` files are in the old OpenStep plist format. When you use the standard functionality through Xcode, it automatically converts these to binary plists on build. With the custom bundle of this process, that no longer happens automatically. However, to fix it, it is relatively straightforward. Simply add a new run script phase to your main apps build phases, and add the following line to it:

```bash
find "${TARGET_BUILD_DIR}/${CONTENTS_FOLDER_PATH}/LocalizedStringKit.bundle" -name "LocalizedStringKit.strings" -exec plutil -convert binary1 {} \;
```

On build, the files in your binary will now be compressed. 

### Is this available through Swift Package Manager?
Yes, it is listed on the Swift Package Index [here](https://swiftpackageindex.com/microsoft/LocalizedStringKit)


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
