let step = 1;
let orgs = document.contxt.orgs;

Vue.component('v-select', VueSelect.VueSelect);

Vue.mixin({
  methods: {
  },
  computed: {

  }

});


if (document.getElementById('gc-onboard')) {
  var appOnboard = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-onboard',
    components: {
      'vue-select': 'vue-select'
    },
    data() {
      return {
        step: step,
        isOrg: false,
        orgs: orgs,
        data: {
          bio: '',
          skillsSelected: [],
          jobSelected: [],
          interestsSelected: [],
          userOptions: [],
          orgSelected: [],
          orgOptions: [],
          email: ''
        },
        skills: [],
        interests: [
          'Front End Development',
          'Back End Development',
          'Design',
          'Decentralized Finance',
          'Non-Fungibles & Gaming',
          'Infrastructure & Research',
          `DAO's & Governance`,
          'Marketplaces',
          'Token Economics',
          'Community Building',
          'Gamification',
          'Web3',
          'Freelance Jobs',
          'Healthcare'
        ],
        jobSearchStatus: [
          {
            value: 'AL',
            string: 'I am actively looking for work'
          },
          {
            value: 'PL',
            string: 'I am passively looking and open to hearing new opportunities'
          },
          {
            value: 'N',
            string: 'I am not open to hearing new opportunities'
          }
        ],
      };
    },
    computed: {
      totalcharacter: function() {
        return this.data.bio.length;
      }
    },
    methods: {
      openModalStep(step) {
        let vm = this;

        vm.step = step;
        vm.$refs['onboard-modal'].openModal();
      },
      goStep(step) {
        let vm = this;

        vm.step = step;
        vm.scrollToTop();
      },
      scrollToTop() {
        let vm = this;

        vm.$refs["onboard-modal"].$el.scrollTo(0,0);
      },
      submitData() {
        let vm = this;
        const apiUrlPersona = '/api/v1/onboard_save/';
        const postPersonaData = fetchData(apiUrlPersona, 'POST', vm.data);

        $.when(postPersonaData).then((response) => {

          if (vm.step === 3 && vm.orgSelected) {
            document.location.href = `/${vm.orgSelected}`
          }

        }).catch((err) => {
          console.log(err);
          _alert('Unable to create a bounty. Please try again later', 'error');
        });
      },
      fetchSkills() {
        let vm = this;
        const apiUrlSkills = `/api/v0.1/profile/${document.contxt.github_handle}/keywords`;
        const getSkillsData = fetchData(apiUrlSkills, 'GET');
        $.when(getSkillsData).then((response) => {
          vm.data.skillsSelected = response.keywords;

        }).catch((err) => {
          console.log(err);
          // _alert('Unable to create a bounty. Please try again later', 'error');
        });
      },
      keywordSearch(search, loading) {
        let vm = this;

        if (search.length < 1) {
          return;
        }

        if (this.timeout) {
          clearTimeout(this.timeout);
        }

        this.timeout = setTimeout(() => {
          loading(true);
          vm.getKeyword(loading, search);
        }, 1000);

      },
      getKeyword: async function(loading, search) {
        let vm = this;
        let myHeaders = new Headers();
        let url = `/api/v0.1/keywords_search/?term=${escape(search)}`;

        myHeaders.append('X-Requested-With', 'XMLHttpRequest');
        return new Promise(resolve => {

          fetch(url, {
            credentials: 'include',
            headers: myHeaders
          }).then(res => {
            res.json().then(json => {
              vm.skills = json;
              resolve();
            });
            if (loading) {
              loading(false);
            }
          });
        });
      },


    },
    mounted() {
      if (
        document.contxt.github_handle &&
        !document.contxt.persona_is_funder &&
        !document.contxt.persona_is_hunter
      ) {
        // show_persona_modal();
      }
      this.$refs['onboard-modal'].openModal();
      this.fetchSkills();
    },
    created() {

    }
  });
}
