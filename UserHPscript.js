function goTo(page) {
  switch (page) {
    case 'user':
      window.location.href = 'user.html';
      break;
    case 'contact':
      window.location.href = 'contact.html';
      break;
    default:
      alert("Not a Valid Page!");
  }
}
