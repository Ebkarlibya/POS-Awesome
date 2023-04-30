<template>
    <v-autocomplete v-model="selectedItem" @focus="onFocus" :items="items" :loading="isLoading" :search-input.sync="search"
        color="white" item-text="value" item-value="value" cache-items :label=doctype clearable outlined return-object
        dense>
        <template v-slot:item="data">
            <template>
                <v-list-item-content>
                    <v-list-item-title v-html="data.item.value"></v-list-item-title>
                    <v-list-item-subtitle v-html="data.item.description"></v-list-item-subtitle>
                </v-list-item-content>
            </template>
        </template>
    </v-autocomplete>
</template>

<script>
export default {
    props: {
        doctype: {},
        filters: {}
    },
    data: () => ({
        items: [],
        selectedItem: null,
        search: "",
        isLoading: false

    }),
    methods: {
        onFocus() {
            this.search = this.search
        }
    },
    watch: {
        search(val) {
            if (this.isLoading) return
            this.isLoading = true
            this.items = []
            this.$emit("update", val)
            frappe.call(
                {
                    method: "frappe.desk.search.search_link",
                    args: {
                        txt: val,
                        doctype: this.doctype,
                        filters: this.filters
                    },
                    callback: (r) => {
                        for (let item of r.results) {
                            this.items.push(item)
                        }
                        this.isLoading = false
                    }
                }
            )
        },
    },
}
</script>