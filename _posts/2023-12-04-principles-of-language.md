---
layout: distill
title: Principles of Programming Languages notes
description: notes for the course CS F301 Principles of Programming Languages
tags: notes
date: 2023-12-04

authors:
  - name: Shreyas V
    url: "https://shreyasvinaya.github.io/folio/"
    affiliations:
      name: BITS Pilani, Goa Campus

toc:
  - name: Rust
    subsections:
      - name: Programming Concepts
      - name: Ownership
      - name: Enums and Pattern Matching
      - name: Packages and Crates
      - name: Traits and Generics
      - name: Error Handling

# Below is an example of injecting additional post-specific styles.
# If you use this post as a template, delete this _styles block.
_styles: >
  .fake-img {
      background: #bbb;
      border: 1px solid rgba(0, 0, 0, 0.1);
      box-shadow: 0 0px 4px rgba(0, 0, 0, 0.1);
      margin-bottom: 12px;
  }
  .fake-img p {
      font-family: monospace;
      color: white;
      text-align: left;
      margin: 12px 0;
      text-align: center;
      font-size: 16px;
  }
---

# Rust

## Programming Concepts

### Variables and Mutability

- Variables are immutable in Rust
- Declare them as `mut` if you want to assign a new value to it
- Variables are locked to the scope
  - They can have diff values in diff scopes
  ```rust
      let x = 5;
      {
          let x = 6;
          println!("The value of x is: {x}");
          # The value of x is: 6
      }
      println!("The value of x is: {x}");
      # The value of x is: 5
  ```
  - This is called shadowing
- The keyword `let` can be used to change type of the variable
  ```rust
      let spaces = "   ";
      let spaces = spaces.len();
  ```

### Data Types

- Rust is a statically typed language, which means that it must know the types of all variables at compile time
- You need not explicitly declare the variable type during declaration
- Supports tuple destructuring like python
- Memory is protected, incorrect index access is not allowed

### Functions

- Use `fn` keyword to declare a function
- Use `->` to specify return type
- functions dont return values, they return expressions

### Comments

- `//` for single line comments
- `/* */` for multiline comments

### Control Flow

- `if` is an expression
- `if` and `else` must return same type
- `if` can be used in `let` statements
- `loop` is an infinite loop
- `while` is a conditional loop

## Ownership

- Central concept that the compiler uses to manage memory safely.
- Each value has a variable that is its owner.
- There can only be one owner at a time. When owner goes out of scope, value will be dropped (freed).
- Borrowing allows accessing data without taking ownership via references. References are immutable by default to avoid data races.
- Slices allow shared, mutable access to contiguous sequences like vectors.

### What is Ownership?

- Memory is managed through a system of ownership with a set of rules that the compiler checks at compile time
- Ownership rules:
  - Each value in Rust has a variable that’s called its owner
  - There can only be one owner at a time
  - When the owner goes out of scope, the value will be dropped
- Rust never automatically creates “deep” copies of your data
- If you want to deeply copy the heap data of the String, not just the stack data, you can use a common method called `clone`
- Stack only data:
  - fixed size
  - popped off the stack when scope ends
- Benefits of Ownership:
  - Prevents Memory Leaks
  - Prevents Dangling pointers
  - makes code more predictable

### References and Borrowing

- References allow you to refer to some value without taking ownership of it
- References are immutable by default but can be made mutable by using `&mut`
- `&` is used to create a reference
- We call having references as function parameters borrowing
- Borrowing is used to allow multiple readers or one writer of data at a time
- References must always be valid
- Valid references:
  - A reference to any value that is still in scope
  - A reference to any value that has been moved to a new scope
- Mutable references have one big restriction: if you have a mutable reference to a value, you can have no other references to that value.
- Dangling references are not allowed in Rust
- Dangerous references:
  - A reference to a value that has gone out of scope
  - A reference to a value that has been freed

### Slices

- Slices let you reference a contiguous sequence of elements in a collection rather than the whole collection
- Slice is a kind of reference, it does not have ownership
- we can slice strings, arrays, vectors

The concepts of ownership, borrowing, and slices ensure memory safety in Rust programs at compile time.

## Enums and Pattern Matching

- Enums are a way of grouping related values so you can use them without spelling mistakes
- Enums can be used to create custom data types

### How are enums different from struct

- Enums are different from structs because you can only have one variant of an enum value at a time
- In an `enum`, each variant can have different types and amounts of associated data.

### Enums:

- Enumerations can encode multiple variants for a type.
- Variants can have different data associated with them.
- Powerful pattern matching allows easy processing of different variants.
- Great for state machines, error handling, and sending messages between parts of a system.

## Packages and Crates:

- Crates are compilation units in Rust - can produce library or binary.
- Crates can be reused by importing them from other crates.
- Packages contain one or more crates for distribution.
- Module system provides private/public boundary within crate.

## Traits and Generics:

- Traits define shared behavior/interfaces that types can implement.
- Generics provide abstraction over types - functions/structs can work for multiple types.
- Combined, they provide flexibility to make code work with multiple types.
- Lifetimes explicitly annotate how references are valid.

## Error Handling:

- Errors are core part of Rust philosophy. No exceptions.
- Enum error variants carry extra context.
- ? operator handles propagating errors up call stack.
- Idiomatic to expect and handle errors rather than ignore.

## Notes

1. Getting Started -> Ignore mostly
2. Common programming concepts important
3. Understanding ownership
   Slice type is important
4. Using structs to structure related data
   1. mildly important chapter. just skim through it
5. Enums and Pattern matching - VERY IMPORTANT
6. Packaging, states and modules // VERY IMPORTANT - how is this different from c++
7. Maps
8. Error Handling Important //difference from Haskell
9. Generic types, traits and Ifetime /MOST IMPORTANT CHAPTER
10. Iterators and closures
11. Smart pointers /IMPORTANT > Exiension of ownership model
12. Just skim over concurrency, not very imp
