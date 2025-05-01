/** @odoo-module **/

/* Copyright 2023 Kencove (https://kencove.com).
 @author Mohamed Alkobrosli <malkobrosly@kencove.com>
 License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
import {Many2OneField} from "@web/views/fields/many2one/many2one_field";
import {ExportDataDialog} from "@web/views/view_dialogs/export_data_dialog";
import {useService} from "@web/core/utils/hooks";

const {onWillDestroy} = owl;

class CustomExportDataDialog extends ExportDataDialog {
    setup() {
        super.setup();
        this.title = this.env._t("Select Data for Indexing");
        // We hack the current model from props obj to avoid patching other methods
        this.swapResModel = this.props.root.resModel;
        this.props.root.resModel = this.props.context.resModel;
        if (this.props.context.exporter_id) {
            this.state.templateId = this.props.context.exporter_id[0];
        }
        // Once we destroy the dialog we return the original value back
        onWillDestroy(() => {
            this.props.root.resModel = this.swapResModel;
        });
    }
    async onUpdateExportTemplate() {
        const oldRec = await this.orm.read(
            "ir.exports",
            [this.state.templateId],
            ["name", "export_fields"]
        );
        let oldLines = [];
        if (
            oldRec.length &&
            oldRec[0].export_fields &&
            oldRec[0].export_fields.length
        ) {
            oldLines = await this.orm.read("ir.exports.line", oldRec[0].export_fields, [
                "name",
            ]);
        }
        // Get list of field names from exportList and existing lines
        const newFieldNames = this.state.exportList.map((field) => field.id);
        const oldFieldMap = Object.fromEntries(
            oldLines.map((line) => [line.name, line.id])
        );
        // Prepare commands
        const fieldCommands = [];
        // Keep or create
        for (const field of this.state.exportList) {
            if (oldFieldMap[field.id]) {
                // Link existing line
                fieldCommands.push([4, oldFieldMap[field.id]]);
            } else {
                // New line to create
                fieldCommands.push([0, 0, {name: field.id}]);
            }
        }
        // Unlink deleted fields
        for (const oldLine of oldLines) {
            if (!newFieldNames.includes(oldLine.name)) {
                fieldCommands.push([3, oldLine.id]); // Unlink and delete
            }
        }
        // Write back to ir.exports
        await this.orm.write("ir.exports", [this.state.templateId], {
            export_fields: fieldCommands,
        });
        this.state.isEditingTemplate = false;
    }
}
CustomExportDataDialog.template = "typesense_ir_exports.CustomExportDataDialog";

class IrExportWidget extends Many2OneField {
    setup() {
        super.setup();
        this.rpc = useService("rpc");
        this.orm = useService("orm");
        this.dialogService = useService("dialog");
    }
    async downloadExport() {
        return true;
    }
    async getExportedFields(model, import_compat, parentParams) {
        model = this.props.record.data.model_name;
        return await this.rpc("/web/export/get_fields", {
            ...parentParams,
            model,
            import_compat,
        });
    }
    async onExportData() {
        const dialogProps = {
            context: {
                ...this.props.record.context,
                resModel: this.props.record.data.model_name,
                exporter_id: this.props.record.data.exporter_id,
            },
            defaultExportList: [],
            download: this.downloadExport.bind(this),
            getExportedFields: this.getExportedFields.bind(this),
            root: this.props.record.model.root,
        };
        this.dialogService.add(CustomExportDataDialog, dialogProps);
    }
    openIrExport() {
        this.onExportData();
    }
}

IrExportWidget.template = "typesense_ir_exports.IrExportWidget";

registry.category("fields").add("ir_export_widget", IrExportWidget);
