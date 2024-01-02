'''
95-888 C1
Group C4
    Matt McMonagle - mmcmonag
    Paris Chen - danyang2
    Yongbo Li - yongbol
    Yufei Lei - yufeilei

This module contains the code to display graphical statistics
of the salaries.
'''

import pandas as pd
import matplotlib.pyplot as plt


def stat_salary_dist(merged_all_df):
    fig, axs = plt.subplots(1, 2, figsize=(12, 6), sharey=True)

    axs[0].hist(merged_all_df['min_salary'], bins=20, edgecolor='black', color='aquamarine')
    axs[0].set_title('Minimum Salary Distribution')
    axs[0].set_xlabel('Minimum Salary')
    axs[0].set_ylabel('Count')
    min_salary_stats = merged_all_df['min_salary'].describe()
    textstr = '\n'.join(f'{stat}: {min_salary_stats[stat]:.2f}' for stat in min_salary_stats.index)
    axs[0].text(0.75, 0.95, textstr, transform=axs[0].transAxes, fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))


    axs[1].hist(merged_all_df['max_salary'], bins=20, edgecolor='black', color='dodgerblue')
    axs[1].set_title('Maximum Salary Distribution')
    axs[1].set_xlabel('Maximum Salary')
    max_salary_stats = merged_all_df['max_salary'].describe()
    textstr = '\n'.join(f'{stat}: {max_salary_stats[stat]:.2f}' for stat in max_salary_stats.index)
    axs[1].text(0.75, 0.95, textstr, transform=axs[1].transAxes, fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.show()