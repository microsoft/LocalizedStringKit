// Invalid: Using variable instead of string literal
class TestClass {
    let myVar = "test"
    let invalid = Localized(myVar, "Comment")
}
