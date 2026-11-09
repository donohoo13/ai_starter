---
applies-to:
  - "**/*.{rb,rbs,rake,erb,jbuilder}"
  - "**/Gemfile"
  - "**/*.gemspec"
  - "**/Rakefile"
  - "**/config.ru"
  - "**/.rubocop.yml"
  - "**/.standard.yml"
  - "mise.toml"
---

# Ruby conventions

Ruby code reads like its intent: conventional idioms, least surprise, and names that make comments unnecessary.
These are strong defaults rather than hard rules; a departure that reads better for the code at hand is fine.
The Rails section applies only when the project uses Rails.

## Tooling

- **RuboCop**: Code passes the project's `.rubocop.yml` or `.standard.yml` with no new offenses, so the editor's LSP reports nothing on a changed line.

## Types

- **RBS**: Types live in `.rbs` signature files, never in type comments inside application code.
  `rbs prototype rb` generates a skeleton to refine.

## Language

- **Method parentheses**: Omit them for macros, DSL calls and keyword-like methods (`has_many :posts`, `render :show`, `raise`); use them on every other call that takes arguments (`user.update(status:)`).
- **Ternary**: Use only for a short assignment choosing between two values (`status = active ? "Yes" : "No"`), never for control flow or side effects.
- **`unless`**: Use for a negative condition, as a trailing guard where it fits (`return unless valid?`), and never with an `else` branch.
- **Safe navigation**: Chain nil-safe calls with `&.` (`user&.profile&.avatar`).
- **Hash shorthand**: Omit the value when a key matches a local variable or method name, which needs Ruby 3.1 or later (`redirect_to root_path(user_id:, status:)`).
- **Keyword arguments**: Use keyword arguments instead of positional arguments or an options hash when a method takes two or more parameters (`def notify(user:, template:)`).

## Rails

These rules apply when the project uses Rails; they are inert otherwise.

- **Nil-safe calls**: Use `&.`, never ActiveSupport's `try` or `try!`.
- **Presence**: Check objects and strings with `present?` and `blank?` (`name.present?`), and relations with `exists?`, `any?` or `empty?`, since `present?` and `blank?` on a relation load every record.
- **DOM IDs**: Target Turbo Stream actions and views with `dom_id(post)`, never an interpolated string like `"post_#{post.id}"`.
