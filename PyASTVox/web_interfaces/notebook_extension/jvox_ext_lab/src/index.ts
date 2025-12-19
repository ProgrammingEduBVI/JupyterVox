import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { requestAPI } from './request';

/**
 * Initialization data for the jvox-lab-ext-screenreader extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jvox-lab-ext-screenreader:plugin',
  description: 'A JupyterLab extension for JVox for screen reading',
  autoStart: true,
  optional: [ISettingRegistry],
  activate: (app: JupyterFrontEnd, settingRegistry: ISettingRegistry | null) => {
    console.log('JupyterLab extension jvox-lab-ext-screenreader is activated!');

    if (settingRegistry) {
      settingRegistry
        .load(plugin.id)
        .then(settings => {
          console.log('jvox-lab-ext-screenreader settings loaded:', settings.composite);
        })
        .catch(reason => {
          console.error('Failed to load settings for jvox-lab-ext-screenreader.', reason);
        });
    }

    requestAPI<any>('hello')
      .then(data => {
        console.log(data);
      })
      .catch(reason => {
        console.error(
          `The jvox_lab_ext_screenreader server extension appears to be missing.\n${reason}`
        );
      });
  }
};

export default plugin;
