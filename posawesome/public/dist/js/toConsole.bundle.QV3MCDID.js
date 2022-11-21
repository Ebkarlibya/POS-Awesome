(() => {
  // ../posawesome/posawesome/public/js/toConsole.bundle.js
  $(function() {
    frappe.realtime.on("toconsole", function(data) {
      data.forEach((element) => {
        console.log(element);
      });
    });
  });
})();
//# sourceMappingURL=toConsole.bundle.QV3MCDID.js.map
