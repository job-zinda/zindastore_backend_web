from django import forms
from django.utils.safestring import mark_safe
import json

from .models import Product


class KeyValueJSONWidget(forms.Widget):
    template_name = None  # Not using Django template file; render inline HTML

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        element_id = attrs.get("id", f"id_{name}")

        # Ensure value is a dict
        data = {}
        if isinstance(value, str):
            try:
                data = json.loads(value) if value else {}
            except Exception:
                data = {}
        elif isinstance(value, dict):
            data = value
        elif value is None:
            data = {}

        # Pre-render rows from existing data
        rows_html = []
        for k, v in data.items():
            rows_html.append(
                f"""
                <div class=\"kv-row\">
                    <input type=\"text\" class=\"kv-key\" placeholder=\"Key\" value={json.dumps(str(k))} />
                    <input type=\"text\" class=\"kv-value\" placeholder=\"Value\" value={json.dumps(str(v))} />
                    <button type=\"button\" class=\"kv-remove\">Remove</button>
                </div>
                """
            )

        rows_html_str = "".join(rows_html)

        # Hidden input holds JSON for form submission
        hidden_input = f"<input type=\"hidden\" name=\"{name}\" id=\"{element_id}\" />"

        # Controls and container
        html = f"""
        <div class=\"kv-json-widget\" data-target=\"{element_id}\">
            <div class=\"kv-rows\">
                {rows_html_str}
            </div>
            <div class=\"kv-actions\">
                <button type=\"button\" class=\"kv-icon-btn kv-add\" title=\"Add field\" aria-label=\"Add field\">
                    <svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\">
                        <line x1=\"12\" y1=\"5\" x2=\"12\" y2=\"19\"></line>
                        <line x1=\"5\" y1=\"12\" x2=\"19\" y2=\"12\"></line>
                    </svg>
                </button>
            </div>
        </div>
        {hidden_input}
        <style>
            /* Container */
            .kv-json-widget {{ border: 1px solid #ddd; padding: 8px; border-radius: 4px; }}
            .kv-json-widget .kv-row {{ display: flex; gap: 8px; margin-bottom: 6px; align-items: center; }}
            .kv-json-widget .kv-row input[type=text] {{ width: 45%; }}
            .kv-json-widget .kv-actions {{ margin-top: 8px; display: flex; gap: 8px; }}

            /* Icon buttons — override admin button defaults */
            .kv-json-widget button.kv-icon-btn {{
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: 28px !important;
                height: 28px !important;
                border: 1px solid #ccc !important;
                border-radius: 6px !important;
                background: #f9f9f9 !important;
                color: #333 !important;
                cursor: pointer !important;
                padding: 0 !important;
                margin: 0 !important;
                box-sizing: border-box !important;
                line-height: 1 !important;
                text-decoration: none !important;
                appearance: none !important;
                -webkit-appearance: none !important;
            }}
            .kv-json-widget button.kv-icon-btn:hover {{ background: #f0f0f0 !important; }}
            .kv-json-widget button.kv-icon-btn:focus {{ outline: 2px solid #6aa0ff !important; outline-offset: 2px; }}
            .kv-json-widget button.kv-icon-btn svg {{ width: 18px; height: 18px; display: block; pointer-events: none; }}
            /* Spacing for remove icon in a row */
            .kv-json-widget .kv-row .kv-remove {{ margin-left: 4px !important; }}
        </style>
        <script>
        (function() {{
            var root = document.currentScript.previousElementSibling.previousElementSibling; // the widget container
            if (!root || !root.classList.contains('kv-json-widget')) {{
                // Fallback: search by data-target id
                var widgets = document.querySelectorAll('.kv-json-widget[data-target="{element_id}"]');
                if (widgets.length) root = widgets[0];
            }}
            if (!root) return;

            var rowsContainer = root.querySelector('.kv-rows');
            var addBtn = root.querySelector('.kv-add');
            var hidden = document.getElementById('{element_id}');

            function addRow(key, value) {{
                var row = document.createElement('div');
                row.className = 'kv-row';
                row.innerHTML = `
                    <input type="text" class="kv-key" placeholder="Key" />
                    <input type="text" class="kv-value" placeholder="Value" />
                    <button type="button" class="kv-icon-btn kv-remove" title="Remove" aria-label="Remove">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                `;
                rowsContainer.appendChild(row);
                if (key !== undefined) row.querySelector('.kv-key').value = key;
                if (value !== undefined) row.querySelector('.kv-value').value = value;
                row.querySelector('.kv-remove').addEventListener('click', function() {{
                    rowsContainer.removeChild(row);
                    serialize();
                }});
                // Update on changes
                row.querySelector('.kv-key').addEventListener('input', serialize);
                row.querySelector('.kv-value').addEventListener('input', serialize);
                serialize();
            }}

            function serialize() {{
                var rows = rowsContainer.querySelectorAll('.kv-row');
                var obj = {{}};
                rows.forEach(function(r) {{
                    var k = r.querySelector('.kv-key').value.trim();
                    var v = r.querySelector('.kv-value').value;
                    if (!k) return;
                    obj[k] = v;
                }});
                hidden.value = JSON.stringify(obj);
            }}

            addBtn.addEventListener('click', function() {{ addRow('', ''); }});

            // Initialize hidden value from pre-rendered inputs
            (function initFromExisting() {{
                var existingRows = rowsContainer.querySelectorAll('.kv-row');
                if (!existingRows.length) return serialize();
                existingRows.forEach(function(r) {{
                    r.querySelector('.kv-remove').addEventListener('click', function() {{
                        rowsContainer.removeChild(r);
                        serialize();
                    }});
                    r.querySelector('.kv-key').addEventListener('input', serialize);
                    r.querySelector('.kv-value').addEventListener('input', serialize);
                }});
                serialize();
            }})();

            // Ensure serialization on form submit
            var form = hidden && hidden.form;
            if (form) {{
                form.addEventListener('submit', serialize);
            }}
        }})();
        </script>
        """
        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        raw = data.get(name)
        if not raw:
            return {}
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
            return {}
        except Exception:
            return {}


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            'specs': KeyValueJSONWidget(),
        }

    def clean_specs(self):
        value = self.cleaned_data.get('specs')
        # Ensure dict
        if not isinstance(value, dict):
            try:
                value = json.loads(value) if value else {}
            except Exception:
                value = {}
        return value
