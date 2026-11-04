export class UserStatsViewModel {
  totalUsers: number = 0;
  activeUsers: number = 0;
  inactiveUsers: number = 0;
  newHires: number = 0;
  onLeave: number = 0;

  constructor(stats?: Partial<UserStatsViewModel>) {
    if (stats) {
      this.totalUsers = stats.totalUsers ?? 0;
      this.activeUsers = stats.activeUsers ?? 0;
      this.inactiveUsers = stats.inactiveUsers ?? 0;
      this.newHires = stats.newHires ?? 0;
      this.onLeave = stats.onLeave ?? 0;
    }
  }
}
