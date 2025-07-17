 buggy.js

 Bug 1: Using '==' which can lead to unexpected type coercion.
function checkValue(val) {
  if (val == 5) {
    return true;
  }
  return false;
}

 Bug 2: This function might try to access a property on a null object, causing a TypeError.
function getUsername(user) {
   What if the user object is null or undefined?
  return user.name;
}

// Bug 3: Classic asynchronous issue. The loop will finish before the timeouts execute.
// All logs will show the same final value for 'i'.
function delayedLoop() {
  for (var i = 0; i < 3; i++) {
    setTimeout(function() {
      console.log('Value of i:', i);
    }, 10);
  }
}

// Bug 4: Function is declared but never used.
function unusedFunction() {
  return "I do nothing.";
}

checkValue("5");
delayedLoop();
