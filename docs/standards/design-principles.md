# Design principles

## General Software Design Principles

### KISS: Keep It Simple, Stupid

The simplest solution that works is usually the right one. When designing a class or choosing between patterns, pick the straightforward approach. If a simple conditional solves the problem instead of a strategy pattern, use the conditional. If a single class handles the job without getting messy, don't split it up.
This is the most commonly violated principle. Over-engineering usually comes from wanting to apply known design patterns: factories, builders, and decorators get introduced when a basic class would work fine. The skill is distinguishing problems that need sophisticated solutions from problems that need simple ones.
The time to add complexity is when simplicity stops working. If a single class grows to 500 lines with ten different responsibilities, refactor. If adding a new payment method means modifying code in five places, introduce a strategy pattern. But start simple.

### DRY: Don't Repeat Yourself

When the same logic appears in multiple places, pull it into one place. If three classes all validate email addresses the same way, create a shared validation method. If two services both need to convert timestamps, put that conversion in a utility function.
The benefit is maintenance. When the email validation rules change, one method gets updated instead of hunting through the codebase for every duplicated copy. When a bug exists in the timestamp conversion, it gets fixed once.
Don't take DRY too far. If two pieces of code look similar but serve different purposes, duplication is often fine. Forcing them to share code creates artificial coupling where changes to one break the other. The test is whether the logic is conceptually the same, not just textually similar.
DRY also conflicts with KISS. Sometimes the simplest solution is to duplicate code in two places rather than build an abstraction. There is no universal answer; the judgment is in weighing the tradeoff. A sound default: "This validation logic will probably appear in multiple places, but it starts in the User class to avoid adding complexity early. Once it is duplicated three or four times, pull it into a shared validator." Balance competing principles instead of following either one blindly.

### YAGNI: You Aren't Gonna Need It

Build what is needed now, not what might be needed later. When designing a parking lot system, don't add support for valet parking and electric vehicle charging stations unless the requirements call for them. Don't make classes extensible in every direction just in case.
The problem with building for future requirements is that the guess is usually wrong. Complexity gets added for scenarios that never happen, and when the actual new requirement arrives, it differs from what was prepared for. The result is dead code that still has to be maintained.
This principle doesn't mean "never think ahead" - it means don't build ahead. Design with extension in mind, but only implement what is needed now. When asked how a design would extend, that is the moment to discuss how it would change under new requirements; the initial design stays limited to what is actually required.

### Separation of Concerns

Different parts of the code handle different responsibilities, and they don't know about each other's internals. The UI layer doesn't contain business logic. The business logic doesn't know how data is stored. The data access layer doesn't format strings for display.

### Deep modules, small interfaces

A module's interface is complexity every caller pays; its implementation is complexity paid once, by whoever maintains it.
So the best modules are deep: a small interface over a lot of behavior, the way a file `read(path)` hides buffering, encodings, permissions, and devices behind one call.
A shallow module has an interface nearly as large as the work it does, so it adds a name to learn without taking any work off the caller.
Its common forms are a function that only forwards its arguments, a class wrapping a single call, and a config object whose every field the caller must set.

Hide decisions, not just code.
When two modules must change together because both know the same format, ordering, or protocol, that knowledge has leaked across the boundary; move it behind one of them.
Pull complexity down: when a module can settle a case itself (a sensible default, a retry, a boundary condition), it settles it rather than pushing a flag or an exception onto every caller.

Splitting is not free.
Each new module adds an interface, so many small pieces that must be understood together cost more than one deeper piece that can be understood alone.
Split along lines where the parts can be understood and changed independently; merge pieces that share knowledge.
The small interface is also the test seam: a deep module is tested through it, so its internals can be restructured without touching a test.
The idea and the vocabulary come from John Ousterhout's _A Philosophy of Software Design_.

### Law of Demeter

Also called the principle of least knowledge. A method only talks to its immediate friends and never reaches through objects to access distant parts of the system. Code like `order.getCustomer().getAddress().getZipCode()` violates the Law of Demeter.
The problem with deep chaining is coupling. The calling code now knows the internal structure of three different objects. If any of them change how they organize their data, the caller breaks. Instead, put a method on Order called `getCustomerZipCode()` that handles the navigation internally.
Method chaining itself is not the problem. Fluent interfaces like `builder.setName("John").setAge(30).build()` are fine because they return the same object type. The issue is specifically when chaining leaks internal structure by traversing through multiple different object types.
This shapes how class methods get defined. Instead of returning complex objects that callers need to dig through, return the specific data they need or provide higher-level methods that do the work.

## Object-Oriented Design Principles (SOLID)

These principles are grouped under the acronym SOLID and apply specifically when designing classes and their relationships. They matter most when a problem calls for a class hierarchy.
SOLID principles come from Java's heyday of deep inheritance hierarchies and interface-heavy design. Outside of Java and C#, excessive application of SOLID is falling out of fashion. Modern languages favor simpler approaches: composition over class hierarchies, functions over interfaces. Don't break KISS by forcing SOLID patterns where simpler solutions work fine. Apply these principles when the problem calls for them, and recognize when complexity is being added for its own sake.

### SRP: Single Responsibility Principle

A class should have one reason to change. If a class mixes multiple concerns, split them. This is the foundation of good class design.

### OCP: Open/Closed Principle

Classes should be open for extension but closed for modification. New behavior gets added without changing existing code. This usually means using interfaces or abstract classes so new implementations can be added without touching the original code.
Every modification to existing code risks breaking things that already work. If the design uses interfaces from the start, adding new functionality becomes a matter of writing new classes that implement those interfaces. The old code never changes, so it can't break.

### LSP: Liskov Substitution Principle

Subclasses must work wherever the base class works. If a method accepts a Bird, passing in a Penguin shouldn't break things even though penguins can't fly. Subclasses can't violate the expectations set by the parent class.
Said differently, if code uses a parent class or interface, it should be able to use any subclass without knowing which specific subclass it is. The subclass can add new behavior, but it can't remove or break behavior that the parent promised. When a subclass throws an exception for a method the parent class provides, that's a red flag for an LSP violation. If a subclass forces callers to add special-case logic (e.g., `if (bird instanceof Penguin)`), LSP is violated.
This comes up when designing class hierarchies. Think carefully about what methods belong in the base class versus subclasses.

### ISP: Interface Segregation Principle

Prefer small, focused interfaces over large, general-purpose ones. Don't force classes to implement methods they don't need. If a class only needs two methods from an interface with ten methods, that interface is too big.
The problem with fat interfaces is that classes are forced to implement methods they'll never use. This leads to empty implementations or methods that throw exceptions, which is a code smell. Split large interfaces into smaller, cohesive ones. Classes can implement multiple small interfaces if they need to, but they're not stuck implementing irrelevant methods.

### DIP: Dependency Inversion Principle

Code depends on abstractions, not concrete implementations. Instead of NotificationService creating an EmailSender directly, it accepts a MessageSender interface through its constructor.
The "inversion" refers to who defines the contract. Normally, business logic conforms to whatever the implementation provides. DIP flips this: define an interface based on what the business logic needs, then have implementations conform to that interface. The implementation adapts to the business logic, not the other way around.
This matters for both testability and flexibility. When NotificationService depends on a concrete EmailSender, it can't be unit tested without sending real emails, and it can't swap to SMS without modifying the service. When it depends on an interface, a mock can be injected for testing or a different implementation for different channels.

## Putting It All Together

These principles don't need to be named constantly. They guide decisions and give a shared vocabulary when a tradeoff needs explaining. They are tools for thinking, not a checklist to recite.
A quick cheat sheet:

### General Principles

- KISS: start simple, add complexity only when needed
- DRY: reduce duplication, simplify maintenance
- YAGNI: build for today, not hypothetical futures
- Separation of Concerns: enable independent testing and changes
- Deep modules: hide a lot of behavior behind a small interface
- Law of Demeter: reduce coupling, hide internal structure

### SOLID Principles

- SRP: keep classes focused on one responsibility
- OCP: support future requirements without modifying existing code
- LSP: prevent brittle hierarchies that break at runtime
- ISP: keep interfaces clean and focused
- DIP: decouple business logic from implementation details
