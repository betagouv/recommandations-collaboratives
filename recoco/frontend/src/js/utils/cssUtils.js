export const addClassIfNotExists = (element, className) => {
  if (!element.classList.contains(className)) {
    element.classList.add(className);
  }
};

export const removeClassIfExists = (element, className) => {
  if (element.classList.contains(className)) {
    element.classList.remove(className);
  }
};

export const removeAndAddClassConditionaly = (
  condition,
  element,
  removeClass,
  addClass
) => {
  if (condition) {
    element.classList.remove(removeClass);
    element.classList.add(addClass);
  } else {
    element.classList.remove(addClass);
    element.classList.add(removeClass);
  }
};
