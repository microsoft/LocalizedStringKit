// Test cases for raw string support in Swift string extraction

// 1. Raw string in first parameter, regular string in second
Localized(#"Raw string value with "quotes""#, "Regular comment")

// 2. Regular string in first parameter, raw string in second  
Localized("Regular value", #"Raw comment with "quotes""#)

// 3. Both parameters as raw strings
Localized(#"Raw value with "quotes""#, #"Raw comment with "quotes""#)

// 4. Multi-hash raw strings
Localized(##"Raw value with #"nested"# quotes"##, "Regular comment")

// 5. Raw string with LocalizedWithBundle
LocalizedWithBundle(#"Raw value"#, "Comment", "bundle.bundle")

// 6. Raw string with LocalizedWithKeyExtension
LocalizedWithKeyExtension(#"Raw value"#, "Comment", "Extension")

// 7. Raw string with LocalizedWithKeyExtensionAndBundle
LocalizedWithKeyExtensionAndBundle(#"Raw value"#, "Comment", "Extension", "bundle.bundle")

// 8. Mixed regular and raw in all positions
LocalizedWithKeyExtensionAndBundle("Regular value", #"Raw comment"#, "Extension", #"Raw bundle"#)

// 9. Raw string with backslashes (should not need escaping)
Localized(#"Path: C:\Program Files\App"#, "Windows path example")

// 10. Raw string with regex pattern
Localized(#"Pattern: \d{3}-\d{3}-\d{4}"#, "Phone number regex")