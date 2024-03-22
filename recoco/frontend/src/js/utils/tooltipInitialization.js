import { Tooltip } from 'bootstrap';

const tooltipTriggerList = document.querySelectorAll(
  '[data-bs-toggle="tooltip"]'
);
[...tooltipTriggerList].map(
  (tooltipTriggerEl) => new Tooltip(tooltipTriggerEl)
);
