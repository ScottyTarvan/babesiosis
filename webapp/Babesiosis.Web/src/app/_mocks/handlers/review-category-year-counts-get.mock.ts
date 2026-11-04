import { MockRegistration } from 'app/_mocks/mock-handler';
import { GetCategoryYearCountsCommand } from 'app/modules/literature-review/commands/get-category-year-counts.command';
import { CategoryYearCountsViewModel } from 'app/modules/literature-review/viewmodels/category-year-counts.viewmodel';

/**
 * Mirrors `GetCategoryYearCountsController`. The counts are a snapshot of the
 * local database (primary category by publication year), 2016 to 2026.
 */
export const reviewCategoryYearCountsGetMock: MockRegistration<GetCategoryYearCountsCommand, CategoryYearCountsViewModel> = {
  route: 'review-category-year-counts-get',
  handler: () => ({
    years: [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026],
    categories: [
      { code: 'ERY', name: 'Erythrocyte injury, haemolysis, anaemia and immune-mediated processes', label: 'Haemolysis', counts: [2, 4, 1, 2, 9, 4, 4, 9, 11, 13, 6] },
      { code: 'INF', name: 'Inflammation, innate/adaptive immunity and immunopathology', label: 'SIRS', counts: [0, 2, 2, 3, 7, 5, 5, 4, 3, 2, 2] },
      { code: 'END', name: 'Endothelium, microcirculation, perfusion and tissue hypoxia', label: 'Perfusion', counts: [0, 0, 0, 1, 2, 2, 1, 1, 0, 1, 1] },
      { code: 'COA', name: 'Coagulation, platelets, immunothrombosis and DIC', label: 'Coagulation', counts: [0, 3, 1, 1, 1, 3, 0, 0, 1, 2, 2] },
      { code: 'REN', name: 'Renal injury and renal function', label: 'Renal', counts: [0, 1, 3, 2, 2, 2, 4, 2, 4, 1, 1] },
      { code: 'PUL', name: 'Pulmonary injury and gas exchange', label: 'Pulmonary', counts: [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1] },
      { code: 'NEU', name: 'Neurological and cerebral disease', label: 'Neurological', counts: [0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 3] },
      { code: 'CAR', name: 'Cardiac injury and haemodynamics', label: 'Cardiac', counts: [0, 2, 0, 0, 0, 0, 1, 0, 3, 1, 1] },
      { code: 'MET', name: 'Hepatic, metabolic, endocrine and acid-base disturbances', label: 'Metabolic', counts: [0, 0, 0, 3, 1, 1, 2, 2, 0, 1, 2] },
      { code: 'OXO', name: 'Oxidative stress, host-parasite interaction, omics and virulence', label: 'Parasite, Omics, Virulence', counts: [0, 2, 0, 1, 1, 5, 1, 3, 1, 3, 3] },
      { code: 'SEV', name: 'Multisystem clinical phenotype, severity and outcome', label: 'Multisystem, Phenotype', counts: [1, 7, 8, 8, 10, 3, 9, 12, 6, 12, 11] },
    ],
  }),
};
