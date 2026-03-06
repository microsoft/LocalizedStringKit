// Invalid: Using expression instead of string literal
class TestClass {
    let invalid = Localized(String(format: "Hello %@", name), "Comment")
}
