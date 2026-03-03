// Auto-dismiss alerts after 5s
document.querySelectorAll('.alert.alert-dismissible').forEach(el => {
  setTimeout(() => {
    const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
    bsAlert.close();
  }, 5000);
});