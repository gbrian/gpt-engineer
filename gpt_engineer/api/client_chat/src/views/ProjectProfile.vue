<template>
  <div class="project-profile flex flex-col gap-5">
    <ProfileHeader />
    <Achievements />
    <LinkedProjects />
    <ContributionGraph />
    <ContributionActivity />
    <SettingsAndCustomization />
  </div>
</template>

<script>
import ProfileHeader from '@/components/board/ProfileHeader.vue';
import Achievements from '@/components/board/Achievements.vue';
import LinkedProjects from '@/components/board/LinkedProjects.vue';
import ContributionGraph from '@/components/board/ContributionGraph.vue';
import ContributionActivity from '@/components/board/ContributionActivity.vue';
import SettingsAndCustomization from '@/components/board/SettingsAndCustomization.vue';

export default {
  components: {
    ProfileHeader,
    Achievements,
    LinkedProjects,
    ContributionGraph,
    ContributionActivity,
    SettingsAndCustomization
  }
}
</script>