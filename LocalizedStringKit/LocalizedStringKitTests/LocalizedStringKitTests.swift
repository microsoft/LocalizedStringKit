//
//  Copyright (c) Microsoft Corporation. All rights reserved.
//

import LocalizedStringKit
import XCTest

class LocalizedStringKitTests: XCTestCase {
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
      XCTAssertEqual(Localized("Not a Localized String", "Done"), "Not a Localized String")
      XCTAssertEqual(LocalizationUnnecessary("Not Needed"), "Not Needed")
    }
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
}
