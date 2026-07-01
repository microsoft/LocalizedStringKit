import CryptoKit
import XCTest
import LocalizedStringKit

final class LocalizedStringKitTests: XCTestCase {

    static var old: [Any]!

    override class func tearDown() {
      UserDefaults.standard.set(old, forKey: "AppleLanguages")
    }

    override class func setUp() {
      old = UserDefaults.standard.array(forKey: "AppleLanguages")
      // force EN locale if simulator is not set to it.
      UserDefaults.standard.set(["en"] + LocalizedStringKitTests.old, forKey: "AppleLanguages")
    }

    func testExample() {
      // Note: if this test fails its likely the device was set to a none EN locale.
      if Locale.current.languageCode == "en" {
        XCTAssertEqual(Localized("Done", "Done"), "Done")
        XCTAssertEqual(Localized("Not a Localized String", "Done"), "Not a Localized String")
        XCTAssertEqual(LocalizationUnnecessary("Not Needed"), "Not Needed")
      }
      else {
        XCTFail("Please add other development language localization tests")
        XCTAssertEqual(Localized("Done", "Done"), "Done")
        XCTAssertEqual(LocalizedWithBundle("Not a Localized String", "Done", "primary"), "Not a Localized String")
        XCTAssertEqual(LocalizationUnnecessary("Not Needed"), "Not Needed")
      }
    }

    func testLocalizedWithKeyExtension() {
        guard Locale.current.languageCode == "en" else {
            XCTFail("Please add other development language localization tests")
            return
        }
        XCTAssertEqual(LocalizedWithKeyExtension("Open", "Open", "Open is a verb"), "Open")
        XCTAssertEqual(
            LocalizedWithKeyExtensionAndBundle(
            "Open",
                "Open",
                "Open is a verb",
                "informationn"
            ),
            "Open"
        )
    }

    func testLocalizedWithBundle() {
        guard Locale.current.languageCode == "en" else {
            XCTFail("Please add other development language localization tests")
            return
        }
        XCTAssertEqual(LocalizedWithBundle("Open", "Open", "info"), "Open")
    }

    func testGetLocalizedStringKitBundle() {
        XCTAssertNil(getLocalizedStringKitBundle("unknown_bundle"))
    }

    /// Regression test for the runtime hash truncation bug. The runtime must
    /// hash the *full* UTF-8 string, not just the first 8 bytes, so that the
    /// key matches the one produced by the generation tool.
    func testKeyForValueMatchesFullStringHash() {
      // A value longer than 8 bytes. The pre-fix implementation truncated the
      // hash input to the pointer size (8 bytes), producing the wrong key.
      let value = "Terms and Conditions"
      XCTAssertEqual(LSKKeyForValue(value, nil), Self.md5Hex(value))
    }

    /// Two values that share their first 8 bytes must produce different keys.
    func testKeyForValueDistinguishesLongStringsSharingPrefix() {
      let keyA = LSKKeyForValue("Settings screen", nil)
      let keyB = LSKKeyForValue("Settings menu", nil)
      XCTAssertNotEqual(keyA, keyB)
    }

    /// The key extension must be included in the hash input.
    func testKeyForValueIncludesKeyExtension() {
      let base = LSKKeyForValue("Schedule", nil)
      let noun = LSKKeyForValue("Schedule", "Noun")
      let verb = LSKKeyForValue("Schedule", "Verb")
      XCTAssertNotEqual(base, noun)
      XCTAssertNotEqual(noun, verb)
    }

    func testPrimaryBundleName() {
      XCTAssertEqual(LSKPrimaryBundleName, "LocalizedStringKit.bundle")
      LSKSetPrimaryBundleName("Other.bundle")
      XCTAssertEqual(LSKPrimaryBundleName, "Other.bundle")
    }

  func testAlternateBundleSearchPath() {
    XCTAssertNil(LSKAlternateBundleSearchPath)
    LSKAlternateBundleSearchPath = NSURL(string: "file://path")
    XCTAssertEqual(LSKAlternateBundleSearchPath, NSURL(string: "file://path"))
  }

  // TODO: LocalizedStringKit statically binds the Locale bundle so we cannot swap locale at runtime, if we need to
  //
  //  func testOtherLanguages() {
  //    // TODO theres better ways to override the apps Locale but we dont offer custom a locale setting yet.
  //    let old = UserDefaults.standard.object(forKey: "AppleLanguages")
  //    UserDefaults.standard.set(["es", "it"], forKey: "AppleLanguages")
  //
  //    XCTAssertEqual(Localized("Accept", "Accept"), "Aceptar")
  //    XCTAssertEqual(Localized("Cancel", "Done"), "Cancelar")
  //
  //    UserDefaults.standard.set(old, forKey: "AppleLanguages")
  //
  //  }

    static var allTests = [
        ("testExample", testExample, testPrimaryBundleName, testAlternateBundleSearchPath),
    ]

    /// Compute the hex-encoded MD5 of a string's UTF-8 bytes, matching the
    /// generation tool's key algorithm.
    static func md5Hex(_ string: String) -> String {
      let digest = Insecure.MD5.hash(data: Data(string.utf8))
      return digest.map { String(format: "%02x", $0) }.joined()
    }
}
