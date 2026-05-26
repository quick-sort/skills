---
name: odoo-18-to-19-migration
description: Checklist and fix patterns for migrating Odoo 18 modules to Odoo 19. Covers deprecated ORM/Python APIs (name_get, _cr/_context, @api.returns, _flush_search, _sql_constraints, _read_group signature), removed field attributes (column_format, deprecated), reserved field names (default), search view XML breaking changes (<group string="Group By"> wrapper, expand attribute, <separator/> in search, searchpanel Char fields), QWeb (t-esc → t-out), field renames (product_uom → product_uom_id), res.groups structure (category_id removed, now uses privilege_id → res.groups.privilege), and XML eval Many2many format ((4, ref(...)) → Command.link(ref(...))). Use whenever the user asks to "migrate to Odoo 19", "check Odoo 19 compatibility", "fix Odoo 18 to 19 issues", "upgrade addon to 19", or works on any Odoo 18 module that needs to run on 19.
---

# Odoo 18 → 19 Migration Skill

Comprehensive checklist for migrating Odoo 18.0 addons to Odoo 19.0. Use this skill to audit a module, identify breaking changes, and apply fixes.

## When to Use

Trigger this skill when the user asks to:

- "Migrate to Odoo 19" / "升级到 Odoo 19"
- "Check Odoo 19 compatibility" / "检查 19 兼容性"
- "Fix Odoo 18 to 19 issues"
- Works on any addon whose `__manifest__.py` version starts with `18.0` and needs to run on 19.

## Audit Workflow

Run these greps from the module root to surface every known breaking change in one pass:

```bash
# Python deprecations
grep -rn 'name_get\b\|@api\.returns\|self\._cr\b\|self\._context\b\|_flush_search\b\|fields_get_keys\b\|get_xml_id\b\|column_format=\|deprecated=' --include="*.py"

# Reserved field name "default" (Odoo 19 reserved)
grep -rn 'default\s*=\s*fields\.' --include="*.py"
grep -rn 'name="default"' --include="*.xml"

# _sql_constraints (warning only, still works)
grep -rn '_sql_constraints\s*=' --include="*.py"

# Search view XML breaking changes
grep -rn 'string="Group By"\|expand="0"\|<separator\|<searchpanel' --include="*.xml"

# QWeb: t-esc → t-out
grep -rn 't-esc=' --include="*.xml"

# Field rename
grep -rn 'product_uom[^_a-z]' --include="*.py" --include="*.xml" --include="*.js"

# JS: deprecated field reference (if module renamed default → is_default)
grep -rn '"default"' --include="*.js"

# res.groups: category_id removed (now uses privilege_id)
grep -rn 'model="res.groups"' --include="*.xml" | xargs grep -l "category_id"

# XML eval: old-style Many2many tuple commands
grep -rn 'eval=.*\(4,' --include="*.xml"
grep -rn 'eval=.*\(3,' --include="*.xml"
```

## Breaking Changes Reference

### A. ORM / Python API

| # | Deprecated | Replacement | Severity |
|---|-----------|-------------|----------|
| 1 | `name_get()` override | Computed field `_compute_display_name` | 🔴 Blocking |
| 2 | `record._cr` | `record.env.cr` | 🔴 Blocking |
| 3 | `record._context` | `record.env.context` | 🔴 Blocking |
| 4 | `@api.returns(...)` decorator | Remove — Odoo infers return type | 🔴 Blocking |
| 5 | `_flush_search()` | `execute_query()` | 🔴 Blocking |
| 6 | `fields_get_keys()` | `list(self._fields)` or equivalent | 🔴 Blocking |
| 7 | `get_xml_id()` | `_get_external_ids()` | 🔴 Blocking |
| 8 | `_read_group()` old signature | New signature (issue #110737) | 🔴 Blocking |
| 9 | `_sql_constraints = [...]` | `models.Constraint` class (attr name MUST start with `_` — see Pattern 8) | 🟡 Warning (still works, but migrate as part of every 19 upgrade) |
| 10 | — | New: `search_fetch()`, `fetch()` for SQL optimization | ➕ Optional |

### B. Field Attributes / Names

| # | Issue | Fix | Severity |
|---|-------|-----|----------|
| 11 | `column_format=` removed | Delete attribute | 🔴 Blocking |
| 12 | `deprecated=` attribute removed | Delete attribute | 🔴 Blocking |
| 13 | Field named `default` (reserved in 19) | Rename → `is_default` (or any non-reserved) | 🔴 Blocking |
| 14 | `product_uom` field reference | Rename → `product_uom_id` | 🔴 Blocking |

### C. XML / Views

| # | Old (18) | New (19) | Severity |
|---|----------|----------|----------|
| 15 | `<group string="Group By">` wrapping filters in `<search>` | Remove wrapper — filters are direct children | 🔴 Blocking |
| 16 | `<group expand="0" ...>` in `<search>` | Remove `expand` attribute | 🔴 Blocking |
| 17 | `<separator />` or `<separator string="..."/>` in `<search>` | Delete — not allowed in search views | 🔴 Blocking |
| 18 | `t-esc="..."` in QWeb | Use `t-out="..."` | 🟡 Phasing out |
| 19 | `<searchpanel><field name="some_char_field"/></searchpanel>` | Only `many2one` / `selection` fields supported | 🔴 Blocking |

### D. Security Groups (`res.groups`)

| # | Old (18) | New (19) | Severity |
|---|----------|----------|----------|
| 23 | `<field name="category_id" ref="..."/>` on `res.groups` | Removed — use `privilege_id` → `res.groups.privilege` | 🔴 Blocking |
| 24 | `res.groups` name unique per `category_id` | Unique per `privilege_id` — names can be shorter ("User", "Manager") | 🔴 Blocking |
| 25 | `implied_ids eval="[(4, ref('...'))]"` | `implied_ids eval="[Command.link(ref('...'))]"` | 🔴 Blocking |
| 26 | `implied_ids eval="[(3, ref('...'))]"` | `implied_ids eval="[Command.unlink(ref('...'))]"` | 🔴 Blocking |

### E. Model Changes

| # | Change | Action |
|---|--------|--------|
| 20 | `hr.employee.base` and `hr.candidate` merged | Update inheritance / field references |
| 21 | `ir.model.fields.translate` deprecated | Use `Selection` with string values |
| 22 | Enterprise views may inherit from removed XMLIDs | Verify inherit IDs still exist |

## Fix Patterns

### Pattern 1 — Search view Group By migration

**Before (18):**
```xml
<search>
    <field name="name" />
    <filter string="Active" name="active" domain="[('active', '=', True)]" />
    <group expand="0" string="Group By">
        <filter string="Provider" name="group_by_provider" context="{'group_by': 'provider_id'}" />
        <separator />
        <filter string="Status" name="group_by_status" context="{'group_by': 'status'}" />
    </group>
</search>
```

**After (19):**
```xml
<search>
    <field name="name" />
    <filter string="Active" name="active" domain="[('active', '=', True)]" />
    <filter string="Provider" name="group_by_provider" context="{'group_by': 'provider_id'}" />
    <filter string="Status" name="group_by_status" context="{'group_by': 'status'}" />
</search>
```

### Pattern 2 — Rename reserved field `default`

When a model declares `default = fields.Boolean(...)`:

1. Rename Python field: `default` → `is_default`
2. Update all XML view references: `<field name="default" />` → `<field name="is_default" />`
3. Update data files (`*.xml`, `*.csv`): `name="default"` → `name="is_default"`
4. Update JS `searchRead` / `read` calls listing `"default"`: → `"is_default"`
5. Update domains: `[('default', '=', True)]` → `[('is_default', '=', True)]`

### Pattern 3 — Context / cr migration

```python
# Before
records = self.env['x'].with_context(self._context).search([])
self._cr.execute("...")

# After
records = self.env['x'].with_context(self.env.context).search([])
self.env.cr.execute("...")
```

### Pattern 4 — Remove `@api.returns`

```python
# Before
@api.returns('self', lambda value: value.id)
def copy(self, default=None):
    ...

# After (just delete decorator)
def copy(self, default=None):
    ...
```

### Pattern 5 — `_message_fetch` override for mail.thread

Odoo 19 changed the signature — add `thread` parameter:

```python
# Before (18)
def _message_fetch(self, domain, search_term=None, before=None, after=None, around=None, limit=30):
    ...

# After (19)
def _message_fetch(self, domain, search_term=None, before=None, after=None, around=None, limit=30, thread=None):
    ...
```

### Pattern 6 — `_thread_to_store` signature

```python
# Before (18)
def _thread_to_store(self, store, request_list=None):
    ...

# After (19) — add fields=None parameter
def _thread_to_store(self, store, fields=None, request_list=None):
    ...
```

### Pattern 7 — JS mail store API

```javascript
// Before (18) — deprecated in 19
await mailStore.fetchData({ thread_id: id });

// After (19) — use orm + insert
const data = await orm.read("mail.thread", [id], [...fields]);
mailStore.insert(data);
```

### Pattern 9 — Security groups `res.groups` migration

Odoo 19 removes `category_id` from `res.groups`. Groups are now organized via `res.groups.privilege`, which sits between `ir.module.category` and `res.groups`.

**Before (18):**
```xml
<odoo>
    <record model="ir.module.category" id="security_mymodule_groups">
        <field name="name">My Module Rights</field>
    </record>

    <record model="res.groups" id="group_mymodule_user">
        <field name="name">My Module User</field>
        <field name="category_id" ref="security_mymodule_groups" />
    </record>

    <record model="res.groups" id="group_mymodule_manager">
        <field name="name">My Module Manager</field>
        <field name="category_id" ref="security_mymodule_groups" />
        <field name="implied_ids" eval="[(4, ref('mymodule.group_mymodule_user'))]" />
    </record>

    <record id="base.group_system" model="res.groups">
        <field name="implied_ids" eval="[(4, ref('mymodule.group_mymodule_manager'))]" />
    </record>
</odoo>
```

**After (19):**
```xml
<odoo>
    <record model="ir.module.category" id="security_mymodule_groups">
        <field name="name">My Module Rights</field>
    </record>

    <!-- New: privilege record links ir.module.category to res.groups -->
    <record model="res.groups.privilege" id="privilege_mymodule">
        <field name="name">My Module</field>
        <field name="category_id" ref="security_mymodule_groups" />
    </record>

    <record model="res.groups" id="group_mymodule_user">
        <field name="name">User</field>  <!-- shorter name: unique within privilege -->
        <field name="privilege_id" ref="privilege_mymodule" />
    </record>

    <record model="res.groups" id="group_mymodule_manager">
        <field name="name">Manager</field>
        <field name="privilege_id" ref="privilege_mymodule" />
        <field name="implied_ids" eval="[Command.link(ref('mymodule.group_mymodule_user'))]" />
    </record>

    <record id="base.group_system" model="res.groups">
        <field name="implied_ids" eval="[Command.link(ref('mymodule.group_mymodule_manager'))]" />
    </record>
</odoo>
```

**Key points:**
- `category_id` on `res.groups` is gone → `ParseError` in Odoo 19 if left
- `ir.module.category` is still created and linked through `res.groups.privilege.category_id`
- Uniqueness constraint is now `(privilege_id, name)` — group names within one privilege must be unique (not across all groups), so shorter names work
- `(4, ref(...))` → `Command.link(ref(...))` in `eval=` for all Many2many fields in XML

### Pattern 10 — XML `eval=` Many2many command format

All old-style tuple commands in XML `eval=` attributes must be replaced:

| Old (18) | New (19) |
|----------|----------|
| `[(4, ref('...'))]` | `[Command.link(ref('...'))]` |
| `[(3, ref('...'))]` | `[Command.unlink(ref('...'))]` |
| `[(5,)]` | `[Command.clear()]` |
| `[(6, 0, [ref('a'), ref('b')])]` | `[Command.set([ref('a'), ref('b')])]` |

```xml
<!-- Old -->
<field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>

<!-- New -->
<field name="implied_ids" eval="[Command.link(ref('base.group_user'))]"/>
```

## Manifest Version Bump

After fixes, bump `__manifest__.py` version prefix:

```python
"version": "19.0.1.0.0",  # was "18.0.x.y.z"
```

## Pattern 8 — `_sql_constraints` → `models.Constraint`

`_sql_constraints` still works in Odoo 19 (deprecation warning only), but the preferred migration is to convert each entry to a `models.Constraint` class attribute.

```python
# Old (works, shows warning)
class MyModel(models.Model):
    _sql_constraints = [
        ("unique_name", "UNIQUE(name)", "Name must be unique"),
        ("positive_qty", "CHECK(qty >= 0)", "Quantity must be positive"),
    ]

# New
from odoo import models

class MyModel(models.Model):
    _unique_name = models.Constraint(
        "UNIQUE(name)",
        "Name must be unique",
    )
    _positive_qty = models.Constraint(
        "CHECK(qty >= 0)",
        "Quantity must be positive",
    )
```

### 🔴 CRITICAL: attribute name must start with `_`

The Python attribute for `models.Constraint` (and `models.Index`) **must** begin with an underscore. Otherwise Odoo raises at class-creation time, *before* the module can install:

```
AssertionError: Names of SQL objects in a model must start with '_'
Error calling __set_name__ on 'Constraint' instance 'unique_name' in 'MyModel'
```

Raised from `odoo/orm/table_objects.py` `__set_name__`. The constraint **name in the DB** is the attribute name without the leading underscore, so `_unique_name` produces a constraint named `unique_name` — matching what `_sql_constraints` would have created. Drop the underscore and the entire module fails to load.

Same rule applies to `models.Index`:
```python
_idx_partner_state = models.Index("(partner_id, state)")
```

## Verification

After applying fixes:

- [ ] All grep patterns above return 0 hits
- [ ] Module loads in Odoo 19 without parse errors or `AssertionError` from `table_objects.py`
- [ ] Search views render with Group By filters at root level
- [ ] No JS console errors referencing renamed fields
- [ ] Manifest version updated to `19.0.x.y.z`
- [ ] Security groups: no `category_id` on `res.groups` records; `res.groups.privilege` created
- [ ] No `(4, ref(...))` tuple commands in XML `eval=` attributes
