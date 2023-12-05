---
layout: distill
title: Principles of Programming Languages notes
description: notes for the course CS F301 Principles of Programming Languages
tags: notes distill
giscus_comments: true
related_posts: false
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

### References and Borrowing
- References allow you to refer to some value without taking ownership of it

### Slices
- Slices let you reference a contiguous sequence of elements in a collection rather than the whole collection

## References