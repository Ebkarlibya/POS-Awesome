<template>
  <div style="max-height: 120px; overflow-y: auto">
    <v-btn
      v-for="groupName in itemGroups"
      :key="groupName"
      medium
      :color="groupName === activeGroup ? 'warning' : 'primary'"
      style="padding: 4px; margin: 0 4px 8px 0"
      @click="triggerSelect($event, groupName)"
    >
      {{ groupName }}
    </v-btn>
  </div>
</template>

<script>
export default {
  name: "ItemGroupMultiSelect",
  props: ["itemGroups", "label"],
  data() {
    return {
      activeGroup: "ALL"
    };
  },
  methods: {
    triggerSelect(event, groupName) {
      this.activeGroup = this.activeGroup === groupName ? "ALL" : groupName;
      this.$emit("click", event, this.activeGroup);
    },
  },
};
</script>
