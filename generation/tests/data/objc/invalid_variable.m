// Invalid: ObjC using variable instead of string literal
@implementation TestClass

- (void)testMethod {
    NSString *myVar = @"test";
    NSString *invalid = [LSKLocalizer localized:myVar comment:@"Comment"];
}

@end
