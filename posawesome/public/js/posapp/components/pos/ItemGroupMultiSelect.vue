<template>
  <div>
    <v-btn
      v-for="groupName in itemGroups"
      :key="groupName"
      medium
      :color="groupName === activeGroup ? 'warning' : 'primary'"
      style="padding: 4px"
      class="ms-2 mb-2"
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
