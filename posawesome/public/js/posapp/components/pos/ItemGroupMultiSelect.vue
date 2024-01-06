<template>
  <div>
    <v-btn
      v-for="groupName in itemGroups"
      :key="groupName"
      medium
      color="primary"
      ref="gBtnRef"
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
  methods: {
    triggerSelect(event, groupName) {
      console.log(event, groupName);
      console.log(this.$refs);
      this.$emit("click", event, groupName);
    },
  },
};
</script>
