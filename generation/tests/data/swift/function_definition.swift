// Function definitions should be ignored (not treated as calls)
class TestClass {
    func LocalizedHelper() { }
    func getLocalizedString() { }

    let valid = Localized("Value", "Comment")
}
