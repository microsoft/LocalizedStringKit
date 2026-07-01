// Invalid: ObjC using variable instead of string literal
@implementation TestClass

- (void)testMethod {
    NSString *myVar = @"test";
    NSString *invalid = Localized(myVar, @"Comment");
}

@end
