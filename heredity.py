import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)
        
    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]

# written by me
def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    result = 0
    no_genes = set()
    for person in people:
        if person not in one_gene and person not in two_genes:
            no_genes.add(person)
            
    no_trait = set()
    for person in people:
        if person not in have_trait:
            no_trait.add(person)
            

    for person in people:

        from_father_chance = 0
        not_from_father_chance = 0
        from_mother_chance = 0
        not_from_mother_chance = 0
        
        # calculating chance for getting it from the mother
        
        if people[person]['mother'] in one_gene:
            from_mother_chance = 0.5
            not_from_mother_chance = 0.5
        if people[person]['mother'] in no_genes:
            from_mother_chance = PROBS['mutation']
            not_from_mother_chance = 1-PROBS['mutation']
        if people[person]['mother'] in two_genes:
            from_mother_chance = 1 - PROBS['mutation']
            not_from_mother_chance = PROBS['mutation']
        
        
        # calculating the chance for getting it from the father
        
        if people[person]['father'] in one_gene:
            from_father_chance = 0.5
            not_from_father_chance = 0.5
        if people[person]['father'] in no_genes:
            from_father_chance = PROBS['mutation']
            not_from_father_chance = 1 - PROBS['mutation']
        if people[person]['father'] in two_genes:
            from_father_chance = 1 - PROBS['mutation']
            not_from_father_chance = PROBS['mutation']

        
        # calculating has trait chances
        
            
        # check how many genes the person has
        
        genes_number = None
        if person in no_genes:
            genes_number = 0
        if person in one_gene:
            genes_number = 1
        if person in two_genes:
            genes_number = 2     
            
        # use probs to tell trait chance
        
        trait_chance = PROBS['trait'][genes_number][True]
        no_trait_chance = PROBS['trait'][genes_number][False]
        
        
        #calculating one gene has trait chances
        
        if person in one_gene and person in have_trait:
            
            # if parents are unknown, get probs
            
            if people[person]['mother'] == None:
                chance = PROBS['gene'][1]
                if result == 0:
                    result = chance * trait_chance
                else:
                    result *= (chance * trait_chance)
            else:

                
                # calculating result

                if result == 0:
                    result = ((from_mother_chance * not_from_father_chance) + (not_from_mother_chance * from_father_chance)) * trait_chance
                else:
                    result *= (((from_mother_chance * not_from_father_chance) + (not_from_mother_chance * from_father_chance)) * trait_chance)


        #calculating one gene no trait chances
        
        if person in one_gene and person in no_trait:
            
            # if parents are unknown, get probs
            
            if people[person]['mother'] == None:
                chance = PROBS['gene'][1]
                if result == 0:
                    result = chance * no_trait_chance
                else:
                    result *= (chance * no_trait_chance)
            else:

                
                # calculating result
                if result == 0:
                    result = ((from_mother_chance * not_from_father_chance) + (not_from_mother_chance * from_father_chance)) * no_trait_chance
                else:
                    result *= (((from_mother_chance * not_from_father_chance) + (not_from_mother_chance * from_father_chance)) * no_trait_chance)
                    
            
        # calculating no gene / trait chances        
            
        if person in no_genes and person in have_trait:
            
            # if parents are unknown, get probs
            
            if people[person]['mother'] == None:
                chance = PROBS['gene'][0]
                if result == 0:
                    result = chance * trait_chance
                else:
                    result *= chance * trait_chance
                    
            else:
                if result == 0:
                    result = (not_from_mother_chance * not_from_father_chance) * trait_chance
                else:
                    result *= ((not_from_mother_chance * not_from_mother_chance) * trait_chance)
                    
                    
        # calculating no gene / no trait chances        
            
        if person in no_genes and person in no_trait:
            
            # if parents are unknown, get probs
            
            if people[person]['mother'] == None:
                chance = PROBS['gene'][0]
                if result == 0:
                    result = chance * no_trait_chance
                else:
                    result *= chance * no_trait_chance
                    
            else:
                if result == 0:
                    result = (not_from_mother_chance * not_from_father_chance) * no_trait_chance
                else:
                    result *= ((not_from_mother_chance * not_from_mother_chance) * no_trait_chance)
                    
                    
                    
        # calculating two genes / trait chance
        
        if person in two_genes and person in have_trait:
        
            if people[person]['mother'] == None:
                chance = PROBS['gene'][2]
                if result == 0:
                    result = chance * trait_chance
                else:
                    result *= chance * trait_chance
                    
            else:
                if result == 0:
                    result = (from_mother_chance * from_father_chance) * trait_chance
                else:
                    result *= ((from_mother_chance * from_father_chance) * trait_chance)
                    
        # calculating two genes / no trait chance
        
        if person in two_genes and person in no_trait:
        
        
            if people[person]['mother'] == None:
                chance = PROBS['gene'][2]
                if result == 0:
                    result = chance * no_trait_chance
                else:
                    result *= chance * no_trait_chance
                    
            else:
                if result == 0:
                    result = (from_mother_chance * from_father_chance) * no_trait_chance
                else:
                    result *= ((from_mother_chance * from_father_chance) * no_trait_chance)
                                        
  
                    
    return result
                    
                    
            
            
                
                    

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    no_genes = set()
    for person in probabilities:
        if person not in one_gene and person not in two_genes:
            no_genes.add(person)
            
    no_trait = set()
    for person in probabilities:
        if person not in have_trait:
            no_trait.add(person)
            
    for person in probabilities:
        if person in no_genes:
            probabilities[person]['gene'][0] += p
            
        if person in one_gene:
            probabilities[person]['gene'][1] += p
            
        if person in two_genes:
            probabilities[person]['gene'][2] += p
            
        if person in have_trait:
            probabilities[person]['trait'][True] += p
            
        if person in no_trait:
           probabilities[person]['trait'][False] += p 
    
    


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    
    for person in probabilities:
        gene_sum = probabilities[person]['gene'][0] + probabilities[person]['gene'][1] + probabilities[person]['gene'][2]
        factor = 1/gene_sum
        
        for i in range(3):
            probabilities[person]['gene'][i] *= factor 
            
        trait_sum = probabilities[person]['trait'][True] + probabilities[person]['trait'][False]
        factor = 1/trait_sum
        probabilities[person]['trait'][True] *= factor
        probabilities[person]['trait'][False] *= factor


if __name__ == "__main__":
    main()
