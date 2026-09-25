import shap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def feature_importance(shap_values, df, file_name):
    '''
    Get the feature importance for the model and the save the plot
    :param shap_values: Shap values
    :param df: Input DataFrame
    :param file_name: Name of the file
    '''
    shap_df = pd.DataFrame(np.abs(shap_values.values),columns=df.columns).mean(axis=0).sort_values(ascending=True)
    shap_df = shap_df.reset_index().rename(columns={'index':'features',0:'mean_abs_shap'})
    shap_df['importance'] = round((shap_df['mean_abs_shap']/shap_df['mean_abs_shap'].sum()) * 100.0,2)
    shap_df_fin = shap_df.query("importance > 1.0").reset_index(drop=True)

    # other features (< 1% importance)
    n_features = len(shap_df.query("importance < 1.0 "))
    shap_df_fin.loc[-1,'features'] = f'other {n_features} features (< % 1 importance)'
    shap_df_fin.loc[-1,'mean_abs_shap'] = shap_df.query("importance < 1.0 ")['mean_abs_shap'].sum()
    shap_df_fin.loc[-1,'importance'] = shap_df.query("importance < 1.0 ")['importance'].sum()
    
    plt.rcParams.update({'font.size':15})
    shap_df_fin[['features','importance']].sort_index().set_index('features').plot(kind='barh')
    plt.gcf().set_size_inches(12,10)
    plt.title("Feature importance (%)")
    plt.xlabel("Importance in %")
    plt.savefig(file_name)

    return None


def model_explain(model, train_data, test_data, file_name, file_name1, file_name2, file_name3):
    '''
    Attain the model explainability and save the plots
    :param model: Model object
    :param train_data: Training data
    :param test_data: Test data
    :param file_name: Name of the file
    :param file_name1: Name of the file
    :param file_name2: Name of the file
    :param file_name3: Name of the file
    '''
    # Global feature importance
    data = train_data.sample(n=100, random_state=123, replace=True)
    explainer = shap.explainers.Permutation(model.predict, data)
    shap_values = explainer(data)
    shap.summary_plot(shap_values, data, plot_type='bar', show=False)
    plt.savefig(file_name1)
    plt.clf()

    # Global feature importance percentage
    feature_importance(shap_values, train_data, file_name)
    plt.clf()

    # Local feature importance
    shap.summary_plot(shap_values, data, show=False)
    plt.savefig(file_name2)
    plt.clf()

    # Individual data explainability
    data = test_data.sample(n=100, random_state=123, replace=True)
    shap_values = explainer(data)
    try:
        shap.waterfall_plot(shap_values[0], show=False) #not applicable for linear model
        plt.savefig(file_name3, bbox_inches='tight')
        plt.clf()
    except:
        pass