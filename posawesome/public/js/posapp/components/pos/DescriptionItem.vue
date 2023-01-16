<template>
    <v-row justify="center">
        <v-dialog v-model="showItemDescDialog" v-if="descriptionItem" persistent width="600">
            <v-card outlined shaped>
                <v-card-title style="user-select: none;">
                    {{ __("Select Item Descriptions") }}
                    <v-spacer></v-spacer>

                    <v-btn color="primary" @click="addDescriptionItem(false)">{{
                        __("Insert")
                    }}</v-btn>
                    <div style="margin-right: 10px;"></div>
                    <v-btn color="error" @click="showItemDescDialog = false">{{
                        __("Close")
                    }}</v-btn>
                </v-card-title>
                <v-card-subtitle v-if="descriptionItem"
                    style="margin: 5px 3px 0px 3px; color: #0097a7 !important; font-size: 18px; user-select: none;">
                    {{ descriptionItem.item_name }}</v-card-subtitle>
                <v-card-subtitle style="user-select: none;">
                    {{ __("Total Qty") }} : {{ descriptionItem.descriptionTotalQty }}
                </v-card-subtitle>

                <v-row style="margin: 0px 15px 0px 15px">
                    <v-col sm="3" v-for="itemDesc in descriptionItem.additional_item_descriptions"
                        @click.stop="incDescItemQty(itemDesc)" @mousedown.stop="fastIncDescItemQty(itemDesc)"
                        @mouseup.stop="clearTimers" @mouseleave.stop="clearTimers">

                        <v-card elevation="2" outlined shaped :key="itemDesc.description" max-height="190px"
                            style="margin: 0px">
                            <v-card-text style="padding: 8px; ">
                                <p primary class="text-center"
                                    style="height: 45px; color: black; font-size: large; user-select: none; margin-bottom: 0px !important">
                                    {{ itemDesc.description }}
                                </p>
                                <!-- <p primary   class="text-center" style="font-size: large; color: black;">
                  {{ itemDesc.selected_qty }}
                </p> -->
                            </v-card-text>
                            <!-- bottom -->
                            <v-card-actions>
                                <v-btn icon large color="secondary" @click.stop="decDescItemQty(itemDesc)"
                                    @mousedown.stop="fastDecDescItemQty(itemDesc)" @mouseup.stop="clearTimers"
                                    @mouseleave.stop="clearTimers" style="margin-start: 5px; margin-end: 10px">
                                    <v-icon>mdi-minus-circle-outline</v-icon>
                                </v-btn>
                                <!-- <v-text-field :label="__('Qty')" hide-details="auto" v-model.number="descriptionItemQty">
                </v-text-field> -->

                                <h4 rounded small primary color="primary" @click.stop="incDescItemQty(itemDesc)"
                                    @mousedown.stop="fastIncDescItemQty(itemDesc)" @mouseup.stop="clearTimers"
                                    @mouseleave.stop="clearTimers"
                                    style="padding-start: 5px; padding-end: 2px; user-select: none;">
                                    {{ itemDesc.selected_qty }}
                                </h4>
                                <!-- <v-btn icon color="secondary"
                  @click.stop="incDescItemQty(itemDesc)"
                  @mousedown.stop="fastIncDescItemQty(itemDesc)"
                  @mouseup.stop="clearTimers"
                  @mouseleave.stop="clearTimers"
                  style="margin-start: 5px; margin-end: 10px">
                  <v-icon>mdi-plus-circle-outline</v-icon>
                </v-btn> -->

                            </v-card-actions>

                        </v-card>
                    </v-col>

                </v-row>
                <v-card-title>
                    <!-- <v-btn color="warning" @click="resetDescriptionItem">{{
          __("Reset")
        }}</v-btn> -->
                    <v-spacer></v-spacer>

                    <v-btn color="primary" @click="addDescriptionItem(false)">{{
                        __("Insert")
                    }}</v-btn>
                    <div style="margin-right: 10px;"></div>
                    <v-btn color="error" @click="showItemDescDialog = false">{{
                        __("Close")
                    }}</v-btn>
                </v-card-title>
            </v-card>
        </v-dialog>
    </v-row>
</template>

<script>
import { evntBus } from '../../bus';
export default {
    data: () => ({
        showItemDescDialog: false,
        descriptionItem: null,
        timeout: null,
        interval: null
    }),
    watch: {},
    methods: {
        hey() {
            console.log("hey");
        },
        incDescItemQty(itemDesc) {
            itemDesc.selected_qty += 1;
            this.descriptionItem.descriptionTotalQty += 1;
            this.$forceUpdate();
        },
        fastIncDescItemQty(itemDesc) {
            this.clearTimers();
            this.timeout = setTimeout(() => {
                this.interval = setInterval(() => {
                    this.incDescItemQty(itemDesc);
                }, 40);
            }, 1000);
        },
        decDescItemQty(itemDesc) {
            if (itemDesc.selected_qty > 0) {
                itemDesc.selected_qty -= 1;
                this.descriptionItem.descriptionTotalQty -= 1;
            }
            this.$forceUpdate();
        },
        fastDecDescItemQty(itemDesc) {
            this.clearTimers();
            this.timeout = setTimeout(() => {
                this.interval = setInterval(() => {
                    this.decDescItemQty(itemDesc);
                }, 40);
            }, 1000);
        },
        clearTimers() {
            clearTimeout(this.timeout);
            clearInterval(this.interval);
        },
        addDescriptionItem(skipQtyValidation = false) {
            // if (this.descriptionItemQty < 0) return;
            let total_qty = 0;

            // debugger
            let descriptionText = "";
            this.descriptionItem.posa_notes = "";

            this.descriptionItem.additional_item_descriptions.forEach((item_desc) => {
                if (item_desc.selected_qty > 0) {
                    total_qty += item_desc.selected_qty;
                    descriptionText += `${item_desc.selected_qty} | ${item_desc.description}\n`;
                }
            });

            if (total_qty === 0 && !skipQtyValidation) {
                frappe.show_alert(frappe._("Please select at least one item"));
                return;
            }

            this.descriptionItem.qty = total_qty;
            this.descriptionItem.posa_notes = descriptionText;

            // reset qty
            evntBus.$emit("add_item", this.descriptionItem, true, descriptionText);
            // this.descriptionItem.posa_notes = "";

            // reset
            setTimeout(() => {
                // this.descriptionItem = null;
                this.showItemDescDialog = false;
                // this.additional_item_descriptions = [];
            }, 100);
        },
        // resetDescriptionItem(){
        //   this.descriptionItem.descriptionTotalQty = 0;
        //   this.descriptionItem.additional_item_descriptions.forEach((item_desc) => {
        //     item_desc.selected_qty = 0;
        //   });
        //   this.$forceUpdate();
        //   this.addDescriptionItem(true);
        // },
        edit_desc_item(item) {
            console.log('child called');
            this.showItemDescDialog = true;
        },
        remove_desc_item(item) {
            this.descriptionItem = null;
            let targetItem = this.items.find((i) => i.item_code === item.item_code);
            targetItem.descriptionTotalQty = 0;
            targetItem.additional_item_descriptions.forEach((item_desc) => {
                item_desc.selected_qty = 0;
            });
        },
    },
    created: function () {
        //   evntBus.$on('open_drafts', (data) => {
        //     this.draftsDialog = true;
        //     this.dialog_data = data;
        //   });
    },
};
</script>
