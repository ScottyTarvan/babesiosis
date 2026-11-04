// Public barrel for Babesiosis's shared front-end code.
//
// The fs-* components, their types, tokens and helpers come from the published
// @fundstream-ai/gnome-ui package (repository fundstream-ai/gnome-ui). This barrel
// re-exports its four entry points so the existing `@core` importers keep compiling;
// new code may import from the package entry points directly. Nothing here is a copy:
// the package is the only source of the components.
//
//   @fundstream-ai/gnome-ui                  every fs-* component without heavy dependencies
//   @fundstream-ai/gnome-ui/chart            fs-chart family and fs-sparkline (apexcharts)
//   @fundstream-ai/gnome-ui/rich-editor      fs-rich-editor and its HTML helpers (tiptap)
//   @fundstream-ai/gnome-ui/layout-designer  fs-layout-designer, fs-layout-view, document model
//
// The rest is Babesiosis's own application code.

export * from '@fundstream-ai/gnome-ui';
export * from '@fundstream-ai/gnome-ui/chart';
export * from '@fundstream-ai/gnome-ui/rich-editor';
export * from '@fundstream-ai/gnome-ui/layout-designer';

export * from 'app/core/pipes/fs-plain-text-excerpt.pipe';
export * from 'app/core/utils/filters';
export * from 'app/core/utils/load-options';
