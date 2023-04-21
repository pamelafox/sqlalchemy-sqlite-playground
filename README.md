[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&repo=pamelafox%2Fflask-db-quiz-example)

This repository includes a small Python Flask web site, made for demonstration purposes only.

To try it out:

1. Open this repository in Codespaces
2. Run the server:

```console
python3 -m flask --debug run
```

2. Click 'http://127.0.0.1:8080' in the terminal, which should open the website in a new tab
3. Try the quiz on the index page, see the high scores update on the bottom.

## Deployment

This repository is set up for deployment on Azure using the configuration files in the `infra` folder.

1. Sign up for a [free Azure account](https://azure.microsoft.com/free/?WT.mc_id=python-79461-pamelafox)
2. Install the [Azure Dev CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd?WT.mc_id=python-79461-pamelafox). (If you open this repository in Codespaces or with the VS Code Dev Containers extension, that part will be done for you.)
3. Initialize a new `azd` environment:

    ```shell
    azd init
    ```

    It will prompt you to provide a name (like "flask-app") that will later be used in the name of the deployed resources.

4. Provision and deploy all the resources:

    ```shell
    azd up
    ```

    It will prompt you to login, pick a subscription, and provide a location (like "eastus"). Then it will provision the resources in your account and deploy the latest code. If you get an error with deployment, changing the location (like to "centralus") can help, as there may be availability constraints for some of the resources.

5. When azd has finished deploying, you'll see an endpoint URI in the command output. Visit that URI and you should see the quiz! 🎉

6. When you've made any changes to the app code, you can just run:

    ```shell
    azd deploy
    ```


