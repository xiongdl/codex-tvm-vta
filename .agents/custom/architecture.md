# Architecture Contract

Prefer the smallest coherent design that satisfies the current approved
requirements.

Optimize for clear ownership, local reasoning, low coupling, small public
surfaces, change locality, and minimal necessary abstraction.

## Ownership

Every important behavior, business rule, and state transition must have one
obvious owner.

A module should have:

- one clear primary responsibility;
- one primary reason to change;
- a small intentional public surface;
- implementation details hidden from consumers.

Feature-specific behavior belongs to the module that owns the feature.

Do not move feature-specific behavior into generic shared modules merely to make
it reusable.

Names such as `utils`, `helpers`, `common`, `manager`, or generic base modules
require a precise responsibility. They are not substitutes for ownership.

## Dependency Direction

Dependencies must follow clear ownership boundaries.

For non-trivial designs, make important dependency direction explicit,
including:

- which module owns the behavior;
- which modules may depend on it;
- important forbidden dependencies;
- where external I/O enters the system.

Avoid circular dependencies.

Keep business rules independent of transport, persistence, serialization,
environment access, and framework-specific infrastructure unless the current
requirements make that dependency necessary.

Do not introduce an interface merely because two modules communicate.

## Public Surface

Default to private or internal.

Expose only what a current consumer requires.

Before adding or broadening a public interface, determine:

1. who consumes it now;
2. what exact capability that consumer needs;
3. whether the surface can be smaller;
4. whether implementation details are being exposed unnecessarily.

Do not add extension points, compatibility layers, or public APIs only for
hypothetical future use.

A larger public surface is a larger coupling surface.

## Abstraction Budget

Every significant abstraction must pay rent.

This applies especially to:

- interfaces;
- services;
- managers;
- repositories;
- factories;
- adapters;
- strategies;
- providers;
- base classes;
- generic helpers;
- wrapper layers.

Before introducing one, answer:

1. What concrete current problem does it solve?
2. Why is direct code insufficient?
3. What concrete complexity does it remove?
4. What becomes worse if the abstraction is removed?

If there is no strong answer, do not add it.

One implementation is not by itself a reason for an interface.

Potential future extensibility is not by itself a reason for an abstraction.

Prefer a few obvious duplicated lines over coupling unrelated concepts through a
premature shared abstraction.

Prefer composition over inheritance unless inheritance represents an intrinsic
relationship required by the design.

## Change Locality

A good boundary localizes likely change.

For important expected changes, identify which modules should need
modification.

Examples include:

- changing a business rule;
- replacing an external provider;
- changing persistence;
- changing transport or presentation;
- adding another implementation of an existing capability.

If one conceptual change requires unrelated modules to change together,
reconsider the ownership or boundary.

Do not optimize the architecture around hypothetical changes with no current
evidence.

## Orchestration and Business Logic

Keep orchestration separate from authoritative business rules when that
separation improves ownership and reasoning.

Transport, CLI, controller, persistence, and infrastructure code should
translate or coordinate at their boundaries rather than become alternate owners
of business behavior.

A layer that provides no policy, translation, ownership, isolation, or boundary
has no architectural reason to exist.

Avoid pass-through layers whose primary behavior is forwarding calls without
adding a meaningful responsibility.

## Structural Simplicity

Prefer explicit and unsurprising structure over indirection.

When two designs satisfy the same requirements, prefer the one with:

- fewer concepts;
- fewer dependencies;
- fewer public contracts;
- fewer ownership boundaries;
- less indirection;
- easier local reasoning.

Do not confuse fewer lines of code with simpler architecture.

Do not split a cohesive responsibility merely to create more modules.

Do not combine unrelated responsibilities merely to reduce the number of
modules.

Complexity should be removed, not relocated.

## Architecture Description

When a change materially affects architecture, its design should make the
following explicit:

### Ownership

Which module owns each important concern.

### Dependencies

Important allowed dependency direction and important forbidden dependencies.

### Public Surface

New or changed public or cross-module contracts.

Anything not intentionally exposed should remain internal.

### Abstractions

For each significant new abstraction:

- the concrete current problem it solves;
- why simpler direct code is insufficient.

### Change Locality

How the most likely changes remain localized.

## Simplification Challenge

Before accepting a design, challenge it:

- Can a module disappear?
- Can an abstraction disappear?
- Can a layer or wrapper disappear?
- Can a public interface become smaller?
- Can ownership become more direct?
- Can a dependency be removed?
- Is complexity being removed or merely moved?
- Is anything justified only by hypothetical future requirements?

Prefer deleting unnecessary concepts over polishing them.
