// Mixed valid and invalid calls
class TestClass {
    let valid1 = Localized("Value1", "Comment1")
    let myVar = "test"
    let invalid = Localized(myVar, "Comment")
    let valid2 = Localized("Value2", "Comment2")
}
