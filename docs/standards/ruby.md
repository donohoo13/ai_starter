---
applies-to:
  - "**/*.{rb,erb,jbuilder}"
  - ".rubocop.yml"
  - ".standard.yml"
  - "config.ru"
  - ".rubocop.yml"
  - "Gemfile"
  - "Rakefile"
  - "mise.toml"
---

# Ruby conventions

Ruby conventions prioritize developer happiness, readability, and poetic expressiveness over rigid system constraints, capturing the philosophy of "least surprise". The community relies heavily on convention over configuration, encouraging standard object-oriented patterns, clean idiom use, and an intuitive syntax that mimics natural English sentence structure. Ultimately the goal is to produce highly maintainable, self-documenting codebases where the underlying intent of the developer/agent is immediately obvious at a glance.

## Tooling

- **LSP & formatting (`Solargraph`/`RuboCop`**: Adhere strictly to the configured `.rubocop.yml` formatting standards to prevent AI-generated code from triggering LSP linting errors (e.g. enforce standard layout rules).
- **Method parentheses**: Omit parentheses for macros, DSLs, and keywords (e.g. `has_many :posts`, `render :show`), but strictly require them for all functional method calls and arguments (e.g. `user.update(status:)`).

## Types

- **Type signatures (`RBS`)**: Rely on RBS files for static typing instead of embedding type comments in application code (e.g. use `rbs prototype rb` to generate types).

## Language

- **Ternary operator**: Use only for brief inline assignments with both outcomes (e.g. `status = active ? "Yes" : "No"`); never use for control flow or side-effect actions.
- **`unless` statement**: Use only for negative logic flow, prioritizing trailing guard clauses (e.g. `return unless valid?`) and never combine it with an `else` branch.
- **Safe navigation**: Use native Ruby safe navigation for nil-safe chaining (e.g. `user&.profile&.avatar`); avoid Rails-specific `try` or `try!`.
- **Presence checking**: (`present?`): Use `present?` / `blank?` on objects or strings (e.g., `name.present?`). but prefer `any?` / `empty?` on ActiveRecord collections to avoid loading unnecessary records.
- **Hotwire dom ID (`dom_id`)**: Use the `dom_id` helper in Turbo Stream actions and view targets (e.g. `dom_id(post)`) instead of manual string interpolation like `"post_#{ post.id }"`.
- **Hash syntax (modern keys)**: Always use Ruby 3+ shorthand hash syntax when variable names match key names (e.g. `redirect_to rootpath(user_id:, status:)`).
- **Keyword arguments**: Prefer strict keyword arguments over positional arguments or open options hashes for complex method signatures (e.g. `def notify(user:, template:)`).
